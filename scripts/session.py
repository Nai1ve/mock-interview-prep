#!/usr/bin/env python3
"""Private, local interview ledger. No network calls or model credentials."""
import argparse
import contextlib
import datetime as dt
import fcntl
import json
import math
import os
from pathlib import Path
import tempfile

STATUSES = {'untested', 'partial', 'demonstrated', 'gap', 'uncertain'}
TYPES = {'question', 'answer', 'assessment', 'source', 'replan', 'finish'}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def atomic(path, content):
    fd, name = tempfile.mkstemp(prefix='.writing-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def save_json(path, value):
    atomic(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def positive(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0


def validate_plan(plan):
    if not isinstance(plan, dict):
        raise ValueError('plan must be an object')
    for key in ('role', 'stage', 'timing_mode', 'timing_basis'):
        if not isinstance(plan.get(key), str) or not plan[key].strip():
            raise ValueError('plan requires ' + key)
    if plan['timing_mode'] not in ('active_estimate', 'wall_clock'):
        raise ValueError('timing_mode must be active_estimate or wall_clock')
    if plan['timing_mode'] == 'wall_clock':
        try:
            deadline = dt.datetime.fromisoformat(plan['deadline'].replace('Z', '+00:00'))
            if deadline.tzinfo is None:
                raise ValueError('deadline requires a timezone')
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError('wall_clock requires a timezone-aware ISO deadline') from exc
    total = plan.get('duration_minutes')
    modules = plan.get('modules')
    if not positive(total) or not isinstance(modules, list) or not modules:
        raise ValueError('positive duration_minutes and nonempty modules required')
    ids = set()
    for module in modules:
        if not isinstance(module, dict) or not module.get('id') or not module.get('name') or not positive(module.get('minutes')):
            raise ValueError('each module requires id, name, positive minutes')
        if module['id'] in ids:
            raise ValueError('duplicate module id')
        ids.add(module['id'])
        if not isinstance(module.get('domains'), list) or not module['domains'] or not all(isinstance(d, str) and d.strip() for d in module['domains']):
            raise ValueError('each module requires domain coverage')
    if not math.isclose(sum(m['minutes'] for m in modules), total, abs_tol=0.001):
        raise ValueError('module minutes must sum to duration_minutes')
    validate_contract(plan)


@contextlib.contextmanager
def locked(folder):
    # A file lock also prevents two agent turns from losing each other's events.
    with (folder / '.lock').open('a', encoding='utf-8') as stream:
        os.chmod(folder / '.lock', 0o600)
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def replay(folder):
    plan = read_json(folder / 'plan.json')
    validate_plan(plan)
    events = []
    for line in (folder / 'events.jsonl').read_text(encoding='utf-8').splitlines():
        if line.strip():
            event = json.loads(line)  # Never silently discard corrupt history.
            if event.get('seq') != len(events) + 1:
                raise ValueError('invalid event sequence')
            events.append(event)
    return plan, events


def projection(plan, events):
    questions = {}
    sources = {}
    elapsed = 0
    current = plan
    finish = None
    for event in events:
        kind = event['type']
        if kind == 'question':
            questions[event['id']] = {**event, 'answer': None, 'assessment': None}
        elif kind == 'answer':
            questions[event['question_id']]['answer'] = event
        elif kind == 'assessment':
            questions[event['question_id']]['assessment'] = event
        elif kind == 'source':
            sources[event['id']] = event
        elif kind == 'replan':
            current = event['plan']
        elif kind == 'finish':
            finish = event
        elapsed = event.get('elapsed_minutes', elapsed)
    coverage = {d: [] for m in current['modules'] for d in m['domains']}
    used = {m['id']: 0 for m in current['modules']}
    previous = 0
    for event in events:
        mark = event.get('elapsed_minutes', previous)
        # The caller attributes time to the module being assessed. Keep missing
        # attribution explicit rather than pretending every minute is measured.
        module = event.get('module_id')
        if module in used:
            used[module] += mark - previous
        previous = mark
    for q in questions.values():
        a = q['assessment']
        coverage.setdefault(q['domain'], []).append({'question_id': q['id'], 'status': a['status'] if a else ('partial' if q['answer'] else 'untested')})
    state = {
        'plan': current, 'original_plan': plan, 'event_count': len(events),
        'elapsed_minutes': elapsed, 'remaining_minutes': max(0, current['duration_minutes'] - elapsed),
        'module_minutes_used': used, 'unattributed_minutes': elapsed - sum(used.values()),
        'questions': list(questions.values()), 'pending_question_ids': [q['id'] for q in questions.values() if q['answer'] is None],
        'coverage': coverage, 'sources': list(sources.values()), 'finish': finish,
    }
    state['selection_audit'] = selection_audit(state)
    return state


def require_text(event, *keys):
    for key in keys:
        if not isinstance(event.get(key), str) or not event[key].strip():
            raise ValueError('event requires ' + key)


def validate_event(event, state):
    if not isinstance(event, dict) or event.get('type') not in TYPES:
        raise ValueError('invalid event type')
    kind = event['type']
    if state['finish'] and kind not in ('assessment', 'source'):
        raise ValueError('session finished; no more questions, answers or replans')
    elapsed = event.get('elapsed_minutes', state['elapsed_minutes'])
    if not isinstance(elapsed, (int, float)) or isinstance(elapsed, bool) or not math.isfinite(elapsed) or elapsed < state['elapsed_minutes']:
        raise ValueError('elapsed_minutes must be finite and monotonic')
    if state['finish'] and elapsed != state['elapsed_minutes']:
        raise ValueError('post-interview review cannot consume assessment time')
    modules = {m['id'] for m in state['plan']['modules']}
    if elapsed != state['elapsed_minutes'] and event.get('module_id') not in modules:
        raise ValueError('time advances require a valid module_id')
    qs = {q['id']: q for q in state['questions']}
    if kind == 'question':
        require_text(event, 'id', 'text', 'module_id', 'domain', 'question_type', 'evidence_goal')
        if event['id'] in qs or event['module_id'] not in modules:
            raise ValueError('duplicate question id or unknown module')
        if state['pending_question_ids']:
            raise ValueError('answer the pending question before asking another')
        if not event.get('resume_claim_ids') and not event.get('jd_requirement'):
            raise ValueError('question must link to resume claim IDs or a JD requirement')
        if event.get('parent_id') and event['parent_id'] not in qs:
            raise ValueError('unknown parent question')
        validate_selection(event, state, elapsed)
        if elapsed >= state['plan']['duration_minutes']:
            raise ValueError('assessment budget exhausted; finish instead')
        if state['plan']['timing_mode'] == 'wall_clock':
            deadline = dt.datetime.fromisoformat(state['plan']['deadline'].replace('Z', '+00:00'))
            if dt.datetime.now(dt.timezone.utc) >= deadline:
                raise ValueError('wall-clock deadline reached; finish instead')
    elif kind in ('answer', 'assessment'):
        require_text(event, 'question_id')
        q = qs.get(event['question_id'])
        if not q:
            raise ValueError('unknown question')
        if kind == 'answer':
            require_text(event, 'text')
            if q['answer']:
                raise ValueError('answer already recorded; use a new follow-up question for a retry')
        else:
            require_text(event, 'evidence', 'decision', 'reason')
            if not q['answer']:
                raise ValueError('cannot assess an unanswered question')
            if event.get('status') not in STATUSES or event['decision'] not in ('deepen', 'branch', 'move_on', 'end'):
                raise ValueError('invalid assessment status or decision')
            if state['plan'].get('schema_version', 1) >= 2:
                require_text(event, 'depth_evidence', 'remaining_unknowns')
                if event.get('observed_depth') not in DEPTHS:
                    raise ValueError('assessment requires observed_depth')
    elif kind == 'source':
        require_text(event, 'id', 'query', 'title', 'url', 'retrieved_at', 'version', 'claim')
        if not event['url'].startswith(('https://', 'http://')) or not isinstance(event.get('verified'), bool):
            raise ValueError('source requires HTTP URL and verified boolean')
        if state['plan'].get('schema_version', 1) >= 2:
            if event.get('phase') not in ('preparation', 'live', 'review') or (state['finish'] and event['phase'] != 'review'):
                raise ValueError('source phase must match preparation/live/review timing')
    elif kind == 'replan':
        require_text(event, 'reason')
        validate_plan(event.get('plan'))
        if event['plan']['duration_minutes'] != state['plan']['duration_minutes'] or event['plan']['timing_mode'] != state['plan']['timing_mode'] or event['plan'].get('deadline') != state['plan'].get('deadline'):
            raise ValueError('replan may redistribute the existing budget, not silently extend it')
        if {m['id'] for m in event['plan']['modules']} != modules:
            raise ValueError('preserve module IDs for reliable time accounting')
        if state['plan'].get('schema_version', 1) >= 2:
            old, new = state['plan'], event['plan']
            if event.get('user_scope_change'):
                require_text(event, 'user_scope_change')
            if new.get('schema_version', 1) < 2:
                raise ValueError('cannot downgrade a granular session')
            if old['practice_scope'] != new['practice_scope'] and not event.get('user_scope_change'):
                raise ValueError('scope changes require the actual user request in user_scope_change')
            old_required = {t['id']:t for t in old['topics'] if t['required']}
            new_topics = {t['id']:t for t in new['topics']}
            if not event.get('user_scope_change') and any(i not in new_topics or not new_topics[i]['required'] or new_topics[i]['domain'] != t['domain'] or new_topics[i]['name'] != t['name'] or new_topics[i]['reserve_minutes'] < t['reserve_minutes'] or DEPTHS[new_topics[i]['target_depth']] < DEPTHS[t['target_depth']] for i,t in old_required.items()):
                raise ValueError('cannot silently erase protected topics, reserves or target depth')
    elif kind == 'finish':
        require_text(event, 'reason')


def update(folder, plan, events):
    state = projection(plan, events)
    save_json(folder / 'session.json', state)
    save_json(folder / 'sources.json', state['sources'])
    return state


def render_audit(state):
    plan = state['plan']
    rows = ['# Mock interview report', '', f"Role: {plan['role']} | Stage: {plan['stage']}",
            f"Timing: {plan['timing_mode']} — {plan['timing_basis']}",
            f"Budget: {plan['duration_minutes']} min; used: {state['elapsed_minutes']} min; remaining: {state['remaining_minutes']} min",
            f"Finish reason: {state['finish']['reason']}", '', '## Coverage and timing', '',
            '| Module | Original minutes | Revised minutes | Recorded used minutes |', '|---|---:|---:|---:|']
    original = {m['id']: m['minutes'] for m in state['original_plan']['modules']}
    for m in plan['modules']:
        rows.append(f"| {m['name']} | {original[m['id']]} | {m['minutes']} | {state['module_minutes_used'][m['id']]} |")
    rows += ['', f"Unattributed minutes: {state['unattributed_minutes']}", '', 'Domain evidence (untested is not failed):', '']
    for domain, evidence in state['coverage'].items():
        rows.append(f"- {domain}: " + (', '.join(x['question_id'] + '=' + x['status'] for x in evidence) or 'untested'))
    rows += ['', '## Practice scope, actual project evidence and topic depth', '', '```json', json.dumps(state['selection_audit'], ensure_ascii=False, indent=2), '```']
    rows += ['', '## Question and follow-up ledger', '']
    for q in state['questions']:
        rows += [f"### {q['id']}" + (f" (follow-up to {q['parent_id']})" if q.get('parent_id') else ''), '', q['text'], '',
                 'Candidate answer: ' + (q['answer']['text'] if q['answer'] else 'Not answered'), '',
                 'Assessment evidence: ' + (q['assessment']['evidence'] if q['assessment'] else 'Not assessed'), '']
    rows += ['## Research sources', '']
    for s in state['sources']:
        rows.append(f"- [{s['title']}]({s['url']}) — retrieved {s['retrieved_at']}; version: {s['version']}; verified: {s['verified']}; supports: {s['claim']}")
    if not state['sources']:
        rows.append('No online sources recorded; no claim of current verification.')
    return '\n'.join(rows) + '\n'


def validate_contract(plan):
    if plan.get('schema_version', 1) < 2:
        return
    scope = plan.get('practice_scope', {})
    require_text(scope, 'objective')
    included, excluded = scope.get('included_domains'), scope.get('excluded_domains')
    if not isinstance(included, list) or not included or not isinstance(excluded, list):
        raise ValueError('scope requires included_domains and excluded_domains lists')
    if set(included) & set(excluded):
        raise ValueError('scope includes an excluded domain')
    if not isinstance(plan.get('projects'), list) or not isinstance(plan.get('resume_map'), list):
        raise ValueError('projects and resume_map lists required')
    projects = {p['id'] for p in plan['projects']}
    if len(projects) != len(plan['projects']):
        raise ValueError('duplicate project ID')
    claims = {r['claim_id'] for r in plan['resume_map']}
    if len(claims) != len(plan['resume_map']):
        raise ValueError('duplicate resume claim ID')
    for r in plan['resume_map']:
        require_text(r, 'resume_evidence')
        if r.get('project_id') and r['project_id'] not in projects:
            raise ValueError('unknown project in resume map')
    topics = plan.get('topics')
    if not isinstance(topics, list) or not topics:
        raise ValueError('specific topics required')
    ids, reserves = set(), 0
    for t in topics:
        require_text(t, 'id', 'name', 'domain', 'basis', 'target_depth')
        if t['id'] in ids or t['domain'] not in included or t['target_depth'] not in DEPTHS:
            raise ValueError('duplicate topic or topic outside scope/invalid depth')
        ids.add(t['id'])
        if not isinstance(t.get('required'), bool):
            raise ValueError('topic required must be boolean')
        reserve = t.get('reserve_minutes', 0)
        if not isinstance(reserve, (int, float)) or isinstance(reserve, bool) or not math.isfinite(reserve) or reserve < 0 or (t['required'] and reserve <= 0):
            raise ValueError('required topics need positive protected sampling minutes')
        if t['required']:
            reserves += reserve
    if reserves > plan['duration_minutes']:
        raise ValueError('protected sampling exceeds total budget')
    require_text(plan, 'preparation_research')


DEPTHS = {'touched': 0, 'basic': 1, 'mechanism': 2, 'boundary': 3}


def selection_audit(state):
    plan = state['plan']
    if plan.get('schema_version', 1) < 2:
        return {'legacy': True, 'note': 'No granular scope/depth contract; coarse tags are not verified topic coverage.'}
    questions = state['questions']
    topics = []
    for t in plan['topics']:
        qs = [q for q in questions if q.get('topic_id') == t['id']]
        answered = [q for q in qs if q['answer']]
        assessed = [q for q in answered if q['assessment']]
        best = max((q['assessment'].get('observed_depth', 'touched') for q in assessed), key=lambda d: DEPTHS[d], default='touched')
        topics.append({**t, 'question_ids': [q['id'] for q in qs], 'sampled': bool(answered),
                       'observed_depth': best, 'target_depth_verified': bool(assessed) and DEPTHS[best] >= DEPTHS[t['target_depth']],
                       'statuses': [q['assessment']['status'] for q in assessed]})
    outstanding = [t for t in topics if t['required'] and not t['sampled']]
    projects = []
    for p in plan['projects']:
        actual = [q['id'] for q in questions if q.get('project_id') == p['id'] and q.get('evidence_kind') == 'resume_actual' and q['answer']]
        hypothetical = [q['id'] for q in questions if q.get('project_id') == p['id'] and q.get('evidence_kind') == 'hypothetical']
        projects.append({**p, 'actual_question_ids': actual, 'hypothetical_question_ids': hypothetical})
    warnings = []
    untouched = [p['id'] for p in projects if p.get('priority') == 'critical' and not p['actual_question_ids']]
    if untouched:
        warnings.append('Important projects without actual implementation evidence: ' + ', '.join(untouched))
    below = [t['id'] for t in topics if t['sampled'] and not t['target_depth_verified']]
    if below:
        warnings.append('Sampled topics still below target depth: ' + ', '.join(below))
    return {'practice_scope': plan['practice_scope'], 'topics': topics, 'projects': projects,
            'unsampled_required_topics': [t['id'] for t in outstanding],
            'protected_minutes_remaining': sum(t['reserve_minutes'] for t in outstanding), 'warnings': warnings}


def validate_selection(event, state, elapsed):
    plan = state['plan']
    if plan.get('schema_version', 1) < 2:
        return
    require_text(event, 'topic_id', 'evidence_kind', 'selection_reason')
    topic = next((t for t in plan['topics'] if t['id'] == event['topic_id']), None)
    if not topic or topic['domain'] != event['domain']:
        raise ValueError('question topic/domain must match an in-scope topic')
    if event['evidence_kind'] not in ('resume_actual', 'hypothetical', 'fundamentals'):
        raise ValueError('invalid evidence_kind')
    claims = {r['claim_id']: r for r in plan['resume_map']}
    if any(r not in claims for r in event.get('resume_claim_ids', [])):
        raise ValueError('unregistered resume claim')
    projects = {p['id'] for p in plan['projects']}
    if event.get('project_id') and event['project_id'] not in projects:
        raise ValueError('unregistered project')
    if event['evidence_kind'] == 'resume_actual':
        require_text(event, 'project_id')
        if not any(claims[r].get('project_id') == event['project_id'] for r in event.get('resume_claim_ids', [])):
            raise ValueError('actual project question needs a claim anchored to that project')
    if event.get('parent_id'):
        parent = next(q for q in state['questions'] if q['id'] == event['parent_id'])
        if not parent['assessment']:
            raise ValueError('assess the parent before choosing a follow-up')
    audit = selection_audit(state)
    reserve_other = sum(t['reserve_minutes'] for t in audit['topics'] if t['required'] and not t['sampled'] and t['id'] != event['topic_id'])
    expected = event.get('expected_answer_minutes')
    if not positive(expected):
        raise ValueError('question requires positive expected_answer_minutes including questioning overhead')
    if expected + reserve_other > plan['duration_minutes'] - elapsed + 0.001:
        raise ValueError('question would consume protected sampling time; select an unsampled priority or shorten/replan honestly')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('init'); p.add_argument('--dir', required=True); p.add_argument('--plan', required=True)
    p = sub.add_parser('append'); p.add_argument('--dir', required=True); p.add_argument('--event', required=True)
    p = sub.add_parser('check'); p.add_argument('--dir', required=True)
    p = sub.add_parser('show'); p.add_argument('--dir', required=True)
    p = sub.add_parser('report'); p.add_argument('--dir', required=True); p.add_argument('--review', required=True)
    args = parser.parse_args()
    folder = Path(args.dir).expanduser().resolve()
    try:
        if args.command == 'init':
            plan = read_json(args.plan); validate_plan(plan)
            folder.mkdir(parents=True, mode=0o700, exist_ok=False)
            os.chmod(folder, 0o700)
            with locked(folder):
                save_json(folder / 'plan.json', plan)
                atomic(folder / 'events.jsonl', '')
                result = update(folder, plan, [])
        else:
            with locked(folder):
                plan, events = replay(folder)
                state = projection(plan, events)
                if args.command == 'append':
                    event = read_json(args.event); validate_event(event, state)
                    event = {**event, 'seq': len(events) + 1, 'recorded_at': now()}
                    events.append(event)
                    atomic(folder / 'events.jsonl', ''.join(json.dumps(e, ensure_ascii=False) + '\n' for e in events))
                    result = update(folder, plan, events)
                elif args.command == 'report':
                    if not state['finish']:
                        raise ValueError('finish the interview before publishing reference answers')
                    review = read_json(args.review)
                    # Complete answer coverage is machine-checkable; answer quality
                    # and source correctness still require model/user review.
                    answers = review.get('answers', {})
                    missing = [q['id'] for q in state['questions'] if not isinstance(answers.get(q['id']), dict) or not all(isinstance(answers[q['id']].get(k), str) and answers[q['id']][k].strip() for k in ('critique', 'gaps', 'reference_answer'))]
                    if missing:
                        raise ValueError('review missing critique/gaps/reference_answer for: ' + ', '.join(missing))
                    for key in ('summary', 'study_plan', 'retest_questions', 'reverse_question_suggestions'):
                        require_text(review, key)
                    body = render_audit(state) + '\n## Overall review\n\n' + review['summary'] + '\n'
                    for q in state['questions']:
                        a = answers[q['id']]
                        body += f"\n## Review {q['id']}\n\n### Critique\n\n{a['critique']}\n\n### Gaps\n\n{a['gaps']}\n\n### Complete reference answer\n\n{a['reference_answer']}\n"
                    for key, title in [('study_plan', 'Prioritized study plan'), ('retest_questions', 'Retest questions'), ('reverse_question_suggestions', 'Suggested questions for the real employer')]:
                        body += f'\n## {title}\n\n{review[key]}\n'
                    save_json(folder / 'review.json', review)
                    atomic(folder / 'report.md', body)
                    result = {'report': str(folder / 'report.md'), 'questions_reviewed': len(answers)}
                elif args.command == 'check':
                    result = {'remaining_minutes': state['remaining_minutes'], **state['selection_audit']}
                else:
                    result = update(folder, plan, events)  # Rebuild stale snapshots.
        if args.command in ('init', 'append'):
            result = {key: result[key] for key in ('event_count', 'elapsed_minutes', 'remaining_minutes', 'pending_question_ids')}
            result['session_dir'] = str(folder)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(2, f'Error: {exc}\n')


if __name__ == '__main__':
    main()

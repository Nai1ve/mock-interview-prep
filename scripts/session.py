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
    return {
        'plan': current, 'original_plan': plan, 'event_count': len(events),
        'elapsed_minutes': elapsed, 'remaining_minutes': max(0, current['duration_minutes'] - elapsed),
        'module_minutes_used': used, 'unattributed_minutes': elapsed - sum(used.values()),
        'questions': list(questions.values()), 'pending_question_ids': [q['id'] for q in questions.values() if q['answer'] is None],
        'coverage': coverage, 'sources': list(sources.values()), 'finish': finish,
    }


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
    elif kind == 'source':
        require_text(event, 'id', 'query', 'title', 'url', 'retrieved_at', 'version', 'claim')
        if not event['url'].startswith(('https://', 'http://')) or not isinstance(event.get('verified'), bool):
            raise ValueError('source requires HTTP URL and verified boolean')
    elif kind == 'replan':
        require_text(event, 'reason')
        validate_plan(event.get('plan'))
        if event['plan']['duration_minutes'] != state['plan']['duration_minutes'] or event['plan']['timing_mode'] != state['plan']['timing_mode'] or event['plan'].get('deadline') != state['plan'].get('deadline'):
            raise ValueError('replan may redistribute the existing budget, not silently extend it')
        if {m['id'] for m in event['plan']['modules']} != modules:
            raise ValueError('preserve module IDs for reliable time accounting')
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('init'); p.add_argument('--dir', required=True); p.add_argument('--plan', required=True)
    p = sub.add_parser('append'); p.add_argument('--dir', required=True); p.add_argument('--event', required=True)
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

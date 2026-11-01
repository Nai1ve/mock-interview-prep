"""Synthetic scenarios for focus, sampling reserves, evidence depth and recovery."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('ledger_v2', Path(__file__).resolve().parents[1] / 'scripts/session.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


def plan():
    return {'schema_version': 2, 'role': 'Full-stack engineer', 'stage': 'technical', 'duration_minutes': 30,
            'timing_mode': 'active_estimate', 'timing_basis': 'Estimated active time',
            'practice_scope': {'objective': 'Today practise backend', 'included_domains': ['backend', 'database', 'cache'], 'excluded_domains': ['frontend']},
            'preparation_research': 'Synthetic fixture: no online verification claimed',
            'modules': [{'id': 'core', 'name': 'Backend assessment', 'minutes': 30, 'domains': ['backend', 'database', 'cache']}],
            'projects': [{'id': 'P1', 'name': 'Data scheduler', 'priority': 'critical'}, {'id': 'P2', 'name': 'Agent service', 'priority': 'critical'}],
            'resume_map': [{'claim_id': 'R1', 'project_id': 'P1', 'resume_evidence': 'Owned scheduler recovery'}, {'claim_id': 'R2', 'project_id': 'P2', 'resume_evidence': 'Owned execution state'}],
            'topics': [
                {'id': 'recovery', 'name': 'Recovery coordination', 'domain': 'backend', 'basis': 'R1 actual responsibility', 'required': True, 'reserve_minutes': 4, 'target_depth': 'boundary'},
                {'id': 'index', 'name': 'Index access path', 'domain': 'database', 'basis': 'JD query tuning', 'required': True, 'reserve_minutes': 4, 'target_depth': 'mechanism'},
                {'id': 'lock', 'name': 'Redis lock ownership', 'domain': 'cache', 'basis': 'User requested lock drill', 'required': True, 'reserve_minutes': 4, 'target_depth': 'boundary'}]}


def question(qid='Q1', topic='recovery', domain='backend', project='P1', claim='R1', kind='resume_actual'):
    return {'type': 'question', 'id': qid, 'text': 'How does your recovery mechanism behave when workers overlap?', 'module_id': 'core', 'domain': domain,
            'question_type': 'project', 'evidence_goal': 'Validate actual recovery sequence', 'resume_claim_ids': [claim], 'project_id': project,
            'topic_id': topic, 'evidence_kind': kind, 'selection_reason': 'Probe relevant actual resume claim', 'expected_answer_minutes': 3}


def add(events, event, p):
    state = s.projection(p, events)
    s.validate_event(event, state)
    events.append({**event, 'seq': len(events) + 1})
    return s.projection(p, events)


class SelectionTest(unittest.TestCase):
    def test_fullstack_jd_does_not_override_backend_focus(self):
        p = plan(); s.validate_plan(p)
        q = question(); q['domain'] = 'frontend'
        with self.assertRaisesRegex(ValueError, 'in-scope'):
            s.validate_event(q, s.projection(p, []))
        p['topics'].append({**p['topics'][0], 'id': 'vue', 'domain': 'frontend'})
        with self.assertRaisesRegex(ValueError, 'outside scope'):
            s.validate_plan(p)

    def test_cannot_fake_actual_project_anchor(self):
        p = plan(); q = question(project='P2')
        with self.assertRaisesRegex(ValueError, 'anchored'):
            s.validate_event(q, s.projection(p, []))
        q['resume_claim_ids'] = ['unknown']
        with self.assertRaisesRegex(ValueError, 'unregistered'):
            s.validate_event(q, s.projection(p, []))

    def test_correct_basic_answer_does_not_prove_mechanism_or_other_topics(self):
        p = plan(); events = []; add(events, question(), p)
        add(events, {'type': 'answer', 'question_id': 'Q1', 'text': 'Use an atomic check', 'module_id': 'core', 'elapsed_minutes': 3}, p)
        state = add(events, {'type': 'assessment', 'question_id': 'Q1', 'status': 'demonstrated', 'decision': 'deepen', 'reason': 'Need mechanism evidence',
                             'evidence': 'Correct short statement', 'observed_depth': 'basic', 'depth_evidence': 'Names atomicity only', 'remaining_unknowns': 'Implementation and failure window'}, p)
        audit = state['selection_audit']
        self.assertFalse(audit['topics'][0]['target_depth_verified'])
        self.assertEqual(audit['unsampled_required_topics'], ['index', 'lock'])
        self.assertIn('P2', audit['warnings'][0])

    def test_hypothetical_scene_does_not_cover_actual_second_project(self):
        p = plan(); events = []; add(events, question(project='P2', claim='R2', kind='hypothetical'), p)
        state = add(events, {'type': 'answer', 'question_id': 'Q1', 'text': 'A hypothetical approach'}, p)
        second = state['selection_audit']['projects'][1]
        self.assertEqual(second['actual_question_ids'], [])
        self.assertEqual(second['hypothetical_question_ids'], ['Q1'])

    def test_long_branch_cannot_consume_other_topics_sampling_budget(self):
        p = plan(); events = []; add(events, question(), p)
        add(events, {'type': 'answer', 'question_id': 'Q1', 'text': 'Detailed answer', 'module_id': 'core', 'elapsed_minutes': 21}, p)
        state = add(events, {'type': 'assessment', 'question_id': 'Q1', 'status': 'partial', 'decision': 'branch', 'reason': 'Boundary unclear',
                             'evidence': 'Sequence missing', 'observed_depth': 'basic', 'depth_evidence': 'Basic conclusion', 'remaining_unknowns': 'Interleaving'}, p)
        with self.assertRaisesRegex(ValueError, 'protected'):
            s.validate_event(question('Q2'), state)
        s.validate_event(question('Q2', 'index', 'database', kind='fundamentals'), state)

    def test_replan_cannot_erase_scope_reserves_or_depth_without_user_change(self):
        p = plan(); state = s.projection(p, [])
        changed = copy.deepcopy(p); changed['topics'][1]['required'] = False
        with self.assertRaisesRegex(ValueError, 'silently erase'):
            s.validate_event({'type': 'replan', 'plan': changed, 'reason': 'More UI'}, state)
        changed = copy.deepcopy(p); changed['topics'][0]['target_depth'] = 'basic'
        with self.assertRaisesRegex(ValueError, 'silently erase'):
            s.validate_event({'type': 'replan', 'plan': changed, 'reason': 'Answered quickly'}, state)

    def test_legacy_session_reports_limitations_without_migration(self):
        p = plan(); p.pop('schema_version')
        self.assertTrue(s.projection(p, [])['selection_audit']['legacy'])

    def test_new_session_replays_depth_project_evidence_and_report(self):
        p = plan(); events = []; add(events, question(), p)
        add(events, {'type': 'answer', 'question_id': 'Q1', 'text': 'Concrete synthetic recovery sequence'}, p)
        add(events, {'type': 'assessment', 'question_id': 'Q1', 'status': 'partial', 'decision': 'move_on', 'reason': 'Sample another priority',
                     'evidence': 'Explains mechanism', 'observed_depth': 'mechanism', 'depth_evidence': 'Actual step order provided', 'remaining_unknowns': 'Failure case not checked'}, p)
        add(events, {'type': 'finish', 'reason': 'User stopped early'}, p)
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            s.save_json(folder/'plan.json', p)
            import json
            s.atomic(folder/'events.jsonl', ''.join(json.dumps(e)+'\n' for e in events))
            recovered = s.update(folder, *s.replay(folder))
            self.assertEqual(recovered['selection_audit']['projects'][0]['actual_question_ids'], ['Q1'])
            self.assertFalse(recovered['selection_audit']['topics'][0]['target_depth_verified'])
            self.assertIn('target_depth_verified', s.render_audit(recovered))


if __name__ == '__main__':
    unittest.main()

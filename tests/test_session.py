import copy
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'session.py'
spec = importlib.util.spec_from_file_location('session', SCRIPT)
ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger)


class SessionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.folder = self.root / 'session'
        self.plan = {'role': 'Synthetic engineer', 'stage': 'technical', 'duration_minutes': 20,
                     'timing_mode': 'active_estimate', 'timing_basis': 'Estimated active speech, not wall-clock',
                     'modules': [{'id': 'project', 'name': 'Projects', 'minutes': 10, 'domains': ['backend']},
                                 {'id': 'foundation', 'name': 'Foundations', 'minutes': 10, 'domains': ['database']}]}
        self.call('init', '--plan', self.file('plan.json', self.plan))

    def file(self, name, data):
        p = self.root / name
        p.write_text(json.dumps(data), encoding='utf-8')
        return p

    def call(self, command, *args, fail=False):
        result = subprocess.run([sys.executable, str(SCRIPT), command, '--dir', str(self.folder), *map(str, args)], text=True, capture_output=True)
        if fail:
            self.assertNotEqual(result.returncode, 0)
            return result.stderr
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def append(self, event, fail=False):
        return self.call('append', '--event', self.file('event.json', event), fail=fail)

    def question(self, qid='Q1', parent=None):
        event = {'type': 'question', 'id': qid, 'text': 'How did you verify the change?', 'module_id': 'project',
                 'domain': 'backend', 'question_type': 'project', 'evidence_goal': 'Measurement validity', 'resume_claim_ids': ['R1']}
        if parent:
            event['parent_id'] = parent
        return event

    def answer(self, qid='Q1', elapsed=2):
        return self.append({'type': 'answer', 'question_id': qid, 'text': 'I compared test results, not production.', 'elapsed_minutes': elapsed, 'module_id': 'project'})

    def test_recovery_and_complete_report_including_followups(self):
        self.append(self.question()); self.answer()
        self.append({'type': 'assessment', 'question_id': 'Q1', 'status': 'partial', 'evidence': 'Only test results mentioned', 'decision': 'deepen', 'reason': 'Measurement conditions unclear'})
        self.append(self.question('Q1.1', 'Q1')); self.answer('Q1.1', 4)
        self.append({'type': 'source', 'id': 'S1', 'query': 'synthetic official docs', 'title': 'Test source', 'url': 'https://example.org/docs', 'retrieved_at': '2026-10-28', 'version': 'unknown', 'claim': 'Synthetic claim', 'verified': False})
        (self.folder / 'session.json').write_text('{}')
        (self.folder / 'sources.json').write_text('[]')
        state = self.call('show')
        self.assertEqual(state['event_count'], 6)
        self.assertEqual(state['pending_question_ids'], [])
        self.assertEqual(state['remaining_minutes'], 16)
        self.assertEqual(state['module_minutes_used']['project'], 4)
        self.assertEqual(state['coverage']['database'], [])
        self.assertEqual(state['sources'][0]['verified'], False)
        self.append({'type': 'finish', 'reason': 'User ended early'})
        review = {'answers': {'Q1': {'critique': 'Limited evidence', 'gaps': 'Load unknown', 'reference_answer': 'A complete synthetic explanation.'}},
                  'summary': 'Database was not tested.', 'study_plan': 'Practice measurements.', 'retest_questions': 'How would you measure tails?', 'reverse_question_suggestions': 'Ask about validation practices.'}
        self.assertIn('Q1.1', self.call('report', '--review', self.file('review.json', review), fail=True))
        review['answers']['Q1.1'] = dict(review['answers']['Q1'])
        self.call('report', '--review', self.file('review.json', review))
        report = (self.folder / 'report.md').read_text()
        self.assertIn('follow-up to Q1', report)
        self.assertIn('database: untested', report)
        self.assertIn('Complete reference answer', report)
        self.assertEqual(os.stat(self.folder).st_mode & 0o777, 0o700)
        for p in self.folder.iterdir():
            self.assertEqual(os.stat(p).st_mode & 0o777, 0o600, p.name)

    def test_no_fixed_followup_limit_and_no_duplicate_pending_questions(self):
        self.append(self.question())
        self.append(self.question('Q2'), fail=True)
        self.answer()
        for i in range(1, 6):
            qid = f'Q1.{i}'
            self.append(self.question(qid, 'Q1'))
            self.answer(qid, i + 2)
        self.assertEqual(len(self.call('show')['questions']), 6)
        self.append(self.question(), fail=True)
        self.append({'type': 'answer', 'question_id': 'Q1', 'text': 'duplicate'}, fail=True)

    def test_budget_exhaustion_overrun_and_post_finish_constraints(self):
        self.append(self.question()); self.answer(elapsed=21)
        self.assertEqual(self.call('show')['remaining_minutes'], 0)
        self.assertIn('exhausted', self.append(self.question('Q2'), fail=True))
        self.append({'type': 'finish', 'reason': 'Budget reached; answer ran over'})
        self.append(self.question('Q3'), fail=True)
        self.append({'type': 'assessment', 'question_id': 'Q1', 'status': 'gap', 'evidence': 'Candidate lacks measurement details', 'decision': 'end', 'reason': 'Budget ended'})
        self.append({'type': 'assessment', 'question_id': 'Q1', 'status': 'gap', 'evidence': 'same', 'decision': 'end', 'reason': 'same', 'elapsed_minutes': 22, 'module_id': 'project'}, fail=True)

    def test_replan_preserves_budget_and_time_cannot_move_backwards(self):
        revised = copy.deepcopy(self.plan)
        revised['modules'][0]['minutes'] = 12
        revised['modules'][1]['minutes'] = 8
        self.append({'type': 'replan', 'plan': revised, 'reason': 'More project evidence valuable'})
        self.assertEqual(self.call('show')['plan']['modules'][0]['minutes'], 12)
        revised['duration_minutes'] = 30
        revised['modules'][1]['minutes'] = 18
        self.append({'type': 'replan', 'plan': revised, 'reason': 'Silent extension'}, fail=True)
        self.append(self.question()); self.answer(elapsed=5)
        self.append({'type': 'finish', 'reason': 'done', 'elapsed_minutes': 3, 'module_id': 'project'}, fail=True)
        self.append({'type': 'finish', 'reason': 'done', 'elapsed_minutes': 6}, fail=True)

    def test_deadline_blocks_stale_elapsed_and_report_requires_finish(self):
        plan = copy.deepcopy(self.plan)
        plan['timing_mode'] = 'wall_clock'
        plan['deadline'] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=1)).isoformat()
        ledger.validate_plan(plan)
        state = ledger.projection(plan, [])
        with self.assertRaisesRegex(ValueError, 'deadline'):
            ledger.validate_event(self.question(), state)
        self.assertIn('finish', self.call('report', '--review', self.file('review.json', {}), fail=True))

    def test_question_cannot_advance_itself_past_budget(self):
        question = self.question()
        question['elapsed_minutes'] = 20
        self.assertIn('exhausted', self.append(question, fail=True))

    def test_corruption_is_not_silently_discarded(self):
        (self.folder / 'events.jsonl').write_text('{broken')
        self.assertIn('Error:', self.call('show', fail=True))


if __name__ == '__main__':
    unittest.main()

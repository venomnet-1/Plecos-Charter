import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('checker', ROOT / 'tools/check_ledger.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / 'project'
        shutil.copytree(ROOT / 'examples/pocket-notes', self.project)
        self.events = [json.loads(line) for line in (self.project / 'docs/ledger.jsonl').read_text().splitlines()]

    def save(self):
        for n, event in enumerate(self.events, 1):
            event['id'] = f'E-{n:04d}'
            event['at'] = f'2026-10-01T10:{n:02d}:00Z'
        (self.project / 'docs/ledger.jsonl').write_text('\n'.join(json.dumps(e) for e in self.events) + '\n')

    def rejected(self, message):
        self.save()
        with self.assertRaisesRegex(checker.LedgerError, message):
            checker.validate(self.project)

    def test_complete_example_keeps_failure_and_deferred_issue(self):
        report = checker.validate(self.project)
        self.assertEqual(report['releases'], 1)
        self.assertEqual(report['open_issues'], 1)
        self.assertEqual(report['candidates'], 2)
        self.assertTrue(report['simulation_only'])

    def test_modified_candidate_is_rejected(self):
        p = self.project / 'artifacts/pocket-notes-0.2.0-c2.py'
        p.write_text(p.read_text() + '\n# changed\n')
        with self.assertRaisesRegex(checker.LedgerError, 'hash mismatch'):
            checker.validate(self.project)

    def test_modified_evidence_is_rejected(self):
        (self.project / 'evidence/c2-behavior.txt').write_text('invented pass')
        with self.assertRaisesRegex(checker.LedgerError, 'hash mismatch'):
            checker.validate(self.project)

    def test_missing_scope_approval_is_rejected(self):
        self.events.pop(2)
        self.rejected('not been approved')

    def test_owner_acceptance_cannot_be_attributed_to_assistant(self):
        self.events[11]['actor']['role'] = 'assistant'
        self.rejected('must be attributed to the owner')

    def test_failed_required_check_blocks_acceptance(self):
        self.events[9]['details']['result'] = 'FAIL'
        self.rejected('every required check must PASS')

    def test_not_tested_required_check_blocks_acceptance(self):
        self.events[10]['details']['result'] = 'NOT_TESTED'
        self.rejected('every required check must PASS')

    def test_stale_candidate_evidence_is_rejected(self):
        self.events[9]['details']['candidate'] = 'PN-0.2.0-c1'
        self.rejected('latest candidate')

    def test_release_without_publication_authorization_is_rejected(self):
        self.events.pop(12)
        self.rejected('publication authorization')

    def test_release_destination_cannot_change(self):
        self.events[13]['details']['destination'] = 'https://example.invalid/other'
        self.rejected('destination mismatch')

    def test_revocation_blocks_continued_work(self):
        self.events.insert(3, {'kind': 'authorization_revoked', 'actor': {'name': 'Avery Example', 'role': 'owner'},
          'simulation_only': True, 'summary': 'Withdraw approval', 'scope': 'S-001', 'version': '0.2.0',
          'details': {'approval_ref': 'fictional-revocation'}})
        self.rejected('authority has been revoked')

    def test_new_verification_invalidates_acceptance_and_publication(self):
        rerun = json.loads(json.dumps(self.events[10]))
        self.events.insert(13, rerun)
        self.rejected('release requires acceptance')

    def test_outside_evidence_path_is_rejected(self):
        self.events[9]['details']['evidence']['path'] = '../outside.txt'
        self.rejected('cannot traverse parents')

    def test_symlink_escape_is_rejected(self):
        outside = Path(self.temp.name) / 'outside.txt'
        outside.write_text('external file')
        link = self.project / 'evidence/escape.txt'
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest('symlinks unavailable on this platform')
        self.events[9]['details']['evidence']['path'] = 'evidence/escape.txt'
        self.rejected('escapes project root')

    def test_mixed_simulation_and_real_records_are_rejected(self):
        self.events[11]['simulation_only'] = False
        self.rejected('cannot mix simulated and real')

    def test_malformed_role_is_a_validation_error(self):
        self.events[0]['actor']['role'] = []
        self.rejected('unknown actor role')

    def test_bad_timestamp_is_a_validation_error(self):
        self.events[0]['at'] = '2026-10-01Z'
        (self.project / 'docs/ledger.jsonl').write_text('\n'.join(json.dumps(e) for e in self.events) + '\n')
        with self.assertRaisesRegex(checker.LedgerError, 'UTC timestamp'):
            checker.validate(self.project)

    def test_empty_ledger_has_no_authority(self):
        (self.project / 'docs/ledger.jsonl').write_text('')
        with self.assertRaisesRegex(checker.LedgerError, 'ledger is empty'):
            checker.validate(self.project)

    def test_local_only_closeout_needs_no_publication(self):
        self.events = [e for e in self.events if e['kind'] not in {'publication_authorized', 'release_recorded'}]
        self.save()
        self.assertEqual(checker.validate(self.project)['releases'], 0)

    def test_initializer_never_overwrites_existing_project(self):
        destination = Path(self.temp.name) / 'initialized'
        command = [sys.executable, str(ROOT / 'tools/init_project.py'), str(destination)]
        first = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual((destination / 'docs/ledger.jsonl').read_text(), '')
        second = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(second.returncode, 0)
        self.assertIn('already exists', second.stderr)

if __name__ == '__main__':
    unittest.main()

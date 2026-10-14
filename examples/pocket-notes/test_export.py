"""Verify the exact selected candidate, not a mutable source working copy."""
import importlib.util
import json
import os
from pathlib import Path
import unittest

candidate = Path(os.environ.get('POCKET_NOTES_CANDIDATE',
    str(Path(__file__).parent / 'artifacts/pocket-notes-0.2.0-c2.py')))
spec = importlib.util.spec_from_file_location('candidate_export', candidate)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ExportTests(unittest.TestCase):
    def test_empty_export(self):
        result = json.loads(module.export_notes([]))
        self.assertEqual(result, {'format': 'pocket-notes-1', 'notes': []})
    def test_literal_unicode(self):
        result = module.export_notes([{'title': 'Café', 'body': '雪'}])
        self.assertIn('Café', result)
        self.assertIn('雪', result)
    def test_round_trip_and_order(self):
        notes = [{'title': 'Second', 'body': 'B\nline'}, {'title': 'First', 'body': '"quoted"'}]
        self.assertEqual(json.loads(module.export_notes(notes))['notes'], notes)
    def test_rejects_invalid_input(self):
        for notes in [None, {}, [{'title': '', 'body': 'x'}], [{'title': 'ok', 'body': 3}]]:
            with self.subTest(notes=notes), self.assertRaises(ValueError):
                module.export_notes(notes)

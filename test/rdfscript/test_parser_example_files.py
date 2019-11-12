import unittest

from rdfscript.rdfscriptparser import RDFScriptParser

class TestParseExampleFiles(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()

    def tearDown(self):
        None

    def test_import(self):

        with open("examples/import.rdfsh") as in_file:
            text = in_file.read()

        forms = self.parser.parse(text)

        self.assertEqual(len(forms), 6)

    def test_names(self):

        with open("examples/names.rdfsh") as in_file:
            text = in_file.read()

        forms = self.parser.parse(text)

        self.assertEqual(len(forms), 11)

    def test_prefix(self):

        with open("examples/prefix.rdfsh") as in_file:
            text = in_file.read()

        forms = self.parser.parse(text)

        self.assertEqual(len(forms), 4)

    def test_templates(self):

        with open("examples/templates.rdfsh") as in_file:
            text = in_file.read()

        forms = self.parser.parse(text)

        self.assertEqual(len(forms), 12)

    def test_advanced(self):
        
        with open("examples/advanced.rdfsh") as in_file:
            text = in_file.read()

        forms = self.parser.parse(text)

        self.assertEqual(len(forms), 19)


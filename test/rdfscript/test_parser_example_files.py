import unittest

from rdfscript.parser import Parser


class TestParseExampleFiles(unittest.TestCase):

    def setUp(self):
        self.parser = Parser()

    def tearDown(self):
        None

    def test_names(self):
        with open("examples/names.shb") as in_file:
            text = in_file.read()

        forms = self.parser.parse(text)

        self.assertEqual(len(forms), 11)

    def test_prefix(self):
        with open("examples/prefix.shb") as in_file:
            text = in_file.read()

        forms = self.parser.parse(text)

        self.assertEqual(len(forms), 4)

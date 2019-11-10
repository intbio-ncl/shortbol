import unittest
import ply.lex as leex

import rdfscript.reader as reader

class ReaderStringTest(unittest.TestCase):

    def setUp(self):
        self.reader = leex.lex(module=reader)
        self.reader.at_line_start = True
        self.reader.indent_stack = [0]

    def tearDown(self):
        None

    def test_string_alpha(self):
        self.reader.input('"String"')
        token = self.reader.token()

        self.assertEqual(token.value, "String")
        self.assertEqual(token.type, 'STRING')

    def test_string_alphanumeric(self):
        self.reader.input('"123String123"')
        token = self.reader.token()

        self.assertEqual(token.value, "123String123")
        self.assertEqual(token.type, 'STRING')

    def test_string_with_whitespace(self):
        self.reader.input('"String with whitespace"')
        token = self.reader.token()

        self.assertEqual(token.value, "String with whitespace")
        self.assertEqual(token.type, 'STRING')

    @unittest.skip("Escaping special characters in strings not implemented yet.")
    def test_string_nested_quotes(self):
        self.reader.input('"String "nested" quotations"')
        token = self.reader.token()

        self.assertEqual(token.value, "String \"nested\" quotations")
        self.assertEqual(token.type, 'STRING')

    @unittest.skip("Escaping special characters in strings not implemented yet.")
    def test_string_nested_single_quotes(self):
        self.reader.input('"String \'nested\' single quotations"')
        token = self.reader.token()

        self.assertEqual(token.value, "String \'nested\' single quotations")
        self.assertEqual(token.type, 'STRING')

    def test_string_multiple_strings(self):
        self.reader.input('"String number one" "String number two"')
        first_token = self.reader.token()
        second_token = self.reader.token()

        self.assertEqual(first_token.value, "String number one")
        self.assertEqual(first_token.type, 'STRING')

        self.assertEqual(second_token.value, "String number two")
        self.assertEqual(second_token.type, 'STRING')


if __name__ == '__main__':
    unittest.main()

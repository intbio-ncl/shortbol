import unittest

from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.env import Env
from rdfscript.core import (Name,
                            Uri,
                            Value)


class RuntimeIdentifierTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()

    def tearDown(self):
        None

    def test_localname_unbound(self):
        forms = self.parser.parse("UnboundSymbol")

        env = Env()
        uri = Uri(env.uri)
        uri.extend(Uri('UnboundSymbol'), delimiter='')

        self.assertEqual(forms[0].evaluate(env), uri)

    def test_self(self):
        forms = self.parser.parse("self")

        env = Env()
        expected_value = env.current_self

        self.assertEqual(forms[0].evaluate(env), expected_value)

    def test_self_prefix(self):
        forms = self.parser.parse("self.me")

        env = Env()
        expected_value = Uri(env.current_self.uri + 'me')

        self.assertEqual(forms[0].evaluate(env), expected_value)

        forms = self.parser.parse("self.<me>")
        self.assertEqual(forms[0].evaluate(env), expected_value)

    def test_localname_bound(self):

        script = ("X=\"value\"\n" +
                  "X")
        forms = self.parser.parse(script)

        env = Env()
        expected_value = Value("value")

        self.assertEqual(forms[0].evaluate(env), expected_value)
        self.assertEqual(forms[1].evaluate(env), expected_value)

    def test_qname_symbol_symbol_unbound(self):

        script = ("@prefix p = <http://eg.org/>\n" +
                  "p.UnboundSymbol")
        forms = self.parser.parse(script)

        env = Env()
        uri = Uri('http://eg.org/UnboundSymbol')

        self.assertEqual(forms[0].evaluate(env), Uri('http://eg.org/'))
        self.assertEqual(forms[1].evaluate(env), uri)

    def test_qname_symbol_uri_unbound(self):

        script = ("@prefix p = <http://eg.org/>\n" +
                  "p.<UnboundSymbol>")
        forms = self.parser.parse(script)

        env = Env()
        uri = Uri('http://eg.org/UnboundSymbol')

        self.assertEqual(forms[0].evaluate(env), Uri('http://eg.org/'))
        self.assertEqual(forms[1].evaluate(env), uri)

    def test_qname_uri_uri_unbound(self):

        script = ("<http://eg.org/>.<UnboundSymbol>")
        forms = self.parser.parse(script)

        env = Env()
        uri = Uri('http://eg.org/UnboundSymbol')

        self.assertEqual(forms[0].evaluate(env), uri)

    def test_qname_uri_symbol_unbound(self):

        script = ("<http://eg.org/>.UnboundSymbol")
        forms = self.parser.parse(script)

        env = Env()
        uri = Uri('http://eg.org/UnboundSymbol')

        self.assertEqual(forms[0].evaluate(env), uri)

    def test_qname_symbol_symbol_bound(self):

        script = ("@prefix p = <http://eg.org/>\n" +
                  "p.X=\"value\"\n" +
                  "p.X")
        forms = self.parser.parse(script)

        env = Env()
        expected_value = Value("value")

        self.assertEqual(forms[0].evaluate(env), Uri('http://eg.org/'))
        self.assertEqual(forms[1].evaluate(env), Value('value'))
        self.assertEqual(forms[2].evaluate(env), Value('value'))

    def test_qname_symbol_uri_bound(self):

        script = ("@prefix p = <http://eg.org/>\n" +
                  "p.X=\"value\"\n" +
                  "p.<X>")
        forms = self.parser.parse(script)

        env = Env()
        expected_value = Value("value")

        self.assertEqual(forms[0].evaluate(env), Uri('http://eg.org/'))
        self.assertEqual(forms[1].evaluate(env), Value('value'))
        self.assertEqual(forms[2].evaluate(env), Value('value'))

    def test_qname_uri_uri_bound(self):

        script = ("@prefix p = <http://eg.org/>\n" +
                  "p.X=\"value\"\n" +
                  "<http://eg.org/>.<X>")
        forms = self.parser.parse(script)

        env = Env()
        expected_value = Value("value")

        self.assertEqual(forms[0].evaluate(env), Uri('http://eg.org/'))
        self.assertEqual(forms[1].evaluate(env), Value('value'))
        self.assertEqual(forms[2].evaluate(env), Value('value'))

    def test_qname_uri_symbol_bound(self):

        script = ("@prefix p = <http://eg.org/>\n" +
                  "p.X=\"value\"\n" +
                  "<http://eg.org/>.X")
        forms = self.parser.parse(script)

        env = Env()
        expected_value = Value("value")

        self.assertEqual(forms[0].evaluate(env), Uri('http://eg.org/'))
        self.assertEqual(forms[1].evaluate(env), Value('value'))
        self.assertEqual(forms[2].evaluate(env), Value('value'))

    def test_self_symbol_bound(self):

        script = ("self.v = \"value\"\n" +
                  "self.v\n" +
                  "v")
        forms = self.parser.parse(script)

        env = Env()

        self.assertEqual(forms[0].evaluate(env), Value('value'))
        self.assertEqual(forms[1].evaluate(env), Value('value'))
        self.assertEqual(forms[2].evaluate(env), Value('value'))

    def test_symbol_default_prefix(self):

        script = ("@prefix p = <http://eg.org/>\n" +
                  "@prefix p\n" +
                  "symbol")

        forms = self.parser.parse(script)
        env = Env()

        self.assertEqual(forms[0].evaluate(env), Uri('http://eg.org/'))
        self.assertEqual(forms[1].evaluate(env), Uri('http://eg.org/'))
        self.assertEqual(forms[2].evaluate(env), Uri('http://eg.org/symbol'))

    def test_symbol_default_prefix_bound(self):

        script = ("@prefix p = <http://eg.org/>\n" +
                  "p.symbol = 42\n" +
                  "@prefix p\n" +
                  "symbol")

        forms = self.parser.parse(script)
        env = Env()

        forms[0].evaluate(env)
        forms[1].evaluate(env)
        forms[2].evaluate(env)
        self.assertEqual(forms[3].evaluate(env), Value(42))

    def test_prefixed_symbol_default_prefix(self):

        script = ("@prefix p = <http://eg.org/>\n" +
                  "@prefix q = <http://eg2.org/>\n" +
                  "p.symbol = 42\n" +
                  "q.symbol = 43\n" +
                  "@prefix p\n" +
                  "symbol\n" +
                  "q.symbol")

        forms = self.parser.parse(script)
        env = Env()

        forms[0].evaluate(env)
        forms[1].evaluate(env)
        forms[2].evaluate(env)
        forms[3].evaluate(env)
        forms[4].evaluate(env)
        self.assertEqual(forms[5].evaluate(env), Value(42))
        self.assertEqual(forms[6].evaluate(env), Value(43))

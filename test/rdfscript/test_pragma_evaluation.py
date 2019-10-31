import unittest

from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.env import Env
from rdfscript.core import (Name,
                            Uri,
                            Value)
from rdfscript.pragma import (PrefixPragma,
                              DefaultPrefixPragma,
                              ImportPragma)

from extensions.cardinality import AtLeastOne


class PragmaEvaluateTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()
        self.env = Env()

    def tearDown(self):
        None

    def test_prefix_pragma_name(self):

        uri = Uri('http://prefix.test/')
        name = Name('uri')
        pragma = PrefixPragma('test', Name('uri'))
        self.env.assign(name.evaluate(self.env), uri)
        value = pragma.evaluate(self.env)

        self.assertEqual(value, uri)
        self.assertEqual(self.env.uri_for_prefix('test'), uri)

    def test_prefix_pragma_uri(self):

        uri = Uri('http://prefix.test/')
        pragma = PrefixPragma('test', Name(uri))
        value = pragma.evaluate(self.env)

        self.assertEqual(value, uri)
        self.assertEqual(self.env.uri_for_prefix('test'), uri)

    def test_default_prefix_pragma(self):

        prefix = 'test'
        uri = Uri('http://prefix.test/')
        self.env.bind_prefix(prefix, uri)
        self.assertNotEqual(self.env.prefix, prefix)

        pragma = DefaultPrefixPragma(prefix)
        self.assertEqual(pragma.evaluate(self.env), uri)
        self.assertEqual(self.env.uri, uri)
        self.assertEqual(self.env.prefix, prefix)

    def test_extension_pragma_evaluate_args(self):

        e = self.parser.parse('@extension E(arg)')[0]

        e.evaluate(self.env)

        self.assertEqual(e.args, [Name('arg').evaluate(self.env)])

    def test_python_extension_returns_extension_object(self):

        ext = self.parser.parse('@extension AtLeastOne(uri)')[0]

        expected = AtLeastOne(Name('uri').evaluate(self.env))

        self.assertEqual(expected._prop, ext.as_python_object(self.env)._prop)

    def test_import_pragma_uri(self):

        form = self.parser.parse('use <test/test_files/top>')[0]

        form.evaluate(self.env)
        toptest = Uri('http://top.org/test')
        thisleveltest = Uri('http://thislevel.top/test')
        downthisleveltest = Uri('http://down.thislevel/test')

        self.assertEqual(self.env.lookup(toptest), Value(True))
        self.assertEqual(self.env.lookup(thisleveltest), Value(True))
        self.assertEqual(self.env.lookup(downthisleveltest), Value(True))

    def test_import_pragma_name(self):

        forms = self.parser.parse('x = <test/test_files/top> use x')
        x = forms[0]
        use = forms[1]

        x.evaluate(self.env)
        use.evaluate(self.env)
        toptest = Uri('http://top.org/test')
        thisleveltest = Uri('http://thislevel.top/test')
        downthisleveltest = Uri('http://down.thislevel/test')

        self.assertEqual(self.env.lookup(toptest), Value(True))
        self.assertEqual(self.env.lookup(thisleveltest), Value(True))
        self.assertEqual(self.env.lookup(downthisleveltest), Value(True))

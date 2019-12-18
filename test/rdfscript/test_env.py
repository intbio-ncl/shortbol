import unittest

import sys
import os

sys.path.insert(1, os.path.join(sys.path[0], '..', ".."))

from rdfscript.parser import Parser
from rdfscript.env import Env
from rdfscript.core import (Name,
                            Value,
                            Uri)


class EnvTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()
        self.parser = Parser()

    def tearDown(self):
        None

    def test_prefix_binding(self):

        prefix_uri = Uri('http://test.prefix.eg/')
        prefix = 'prefix'

        self.env.bind_prefix(prefix, prefix_uri)

        self.assertTrue('prefix' in [p for (p, n) in self.env._rdf._g.namespaces()])

    def test_get_and_set_default_prefix(self):

        prefix = 'x'
        self.env.bind_prefix(prefix, Uri('http://eg/'))
        before = Uri(self.env._rdf._g.identifier.toPython())

        
        self.assertEqual(before, self.env.uri)
        self.assertEqual(self.env.prefix, None)

        self.env.prefix = prefix
        self.env.uri = Uri('http://eg/')
        self.assertEqual(Uri('http://eg/'), self.env.uri)
        self.assertEqual('x', self.env.prefix)

    def test_self_uri_set(self):

        uri = Uri('setselfuri')
        self.env.self_uri = uri
        self.assertEqual(self.env.self_uri, uri)

    def test_assignment(self):

        uri = Uri('http://test.variable/#x')
        value = Value(12345)

        self.env.assign(uri, value)
        self.assertEqual(self.env._symbol_table.get(uri), value)

    def test_lookup(self):

        # assume test_assignment passed
        uri = Uri('http://test.variable/#x')
        value = Value(12345)

        self.env.assign(uri, value)
        self.assertEqual(self.env.lookup(uri), value)

    def test_template_binding(self):

        template = self.parser.parse('t()(x = 1 y = 2)')[0]
        uri = template.identifier.evaluate(self.env)
        self.assertFalse(self.env.lookup_template(uri))

        self.env.assign_template(uri, template.as_triples(self.env))
        self.assertEqual(self.env._template_table.get(uri, False),
                         template.as_triples(self.env))

    def test_template_lookup(self):

        template = self.parser.parse('t()(x = 1 y = 2)')[0]
        uri = template.identifier.evaluate(self.env)
        self.assertFalse(self.env.lookup_template(uri))

        self.env._template_table[uri] = template.as_triples(self.env)

        self.assertEqual(self.env.lookup_template(uri),
                         template.as_triples(self.env))

    def test_extension_binding(self):

        t = self.parser.parse('t()(@extension E() @extension F())')[0]
        uri = t.identifier.evaluate(self.env)
        extensions = t.extensions

        self.assertFalse(self.env.lookup_extensions(uri))

        self.env.assign_extensions(uri, extensions)

        self.assertEqual(extensions, self.env._extension_table.get(uri, None))

    def test_extension_lookup(self):

        t = self.parser.parse('t()(@extension E() @extension F())')[0]
        uri = t.identifier.evaluate(self.env)
        extensions = t.extensions

        self.assertFalse(self.env.lookup_extensions(uri))

        self.env._extension_table[uri] = extensions

        self.assertEqual(extensions, self.env.lookup_extensions(uri))


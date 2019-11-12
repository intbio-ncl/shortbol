import unittest
import rdflib

from extensions.triples import TriplePack
from extensions.cardinality import (AtLeastOne,
                                    CardinalityError)
from extensions.error import ExtensionError
from extensions.logic import (And,
                              Or)
from rdfscript.core import (Uri,
                            Value,
                            Name)

from rdfscript.template import (Template,
                                Property,
                                Expansion)
from rdfscript.env import Env

class LogicExtensionsTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()

        self.v_uri = Uri('http://test.triplepack/#variable')
        self.env.assign(self.v_uri,
                        Value(42))

        self.template = Template(Name('A'),
                                  [Name('x'),
                                   Name('y')],
                                  [Property(Name('x'),
                                            Value(42)),
                                   Property(Uri('http://example.eg/predicate'),
                                            Name('y'))])

        self.expansion = Expansion(Name('e'),
                                   Name('A'),
                                   [Value(1),
                                    Value(2)],
                                   [])

        self.template.evaluate(self.env)

        def triple_eval(triple):
            (s, p, o) = triple
            s = s.evaluate(self.env)
            p = p.evaluate(self.env)
            o = o.evaluate(self.env)

            return (s, p, o)

        triples =  self.expansion.as_triples(self.env)
        triples = [triple_eval(triple) for triple in triples]

        bindings = self.env._symbol_table
        templates = self.env._template_table

        self.pack = TriplePack(triples, bindings, templates)

    def test_and_true_true(self):

        true = AtLeastOne(Uri('http://example.eg/predicate', None))

        conjunction = And(true, true)

        triples = list(self.pack.triples)

        conjunction.run(self.pack)

        self.assertEqual(triples, self.pack.triples)

    def test_and_true_false(self):

        true = AtLeastOne(Uri('http://example.eg/predicate', None))
        false = AtLeastOne(Uri('http://test.eg/#notthere', None))

        conjunction = And(true, false)

        triples = list(self.pack.triples)

        with self.assertRaises(ExtensionError):
            conjunction.run(self.pack)

        self.assertEqual(triples, self.pack.triples)

    def test_and_false_true(self):

        true = AtLeastOne(Uri('http://example.eg/predicate', None))
        false = AtLeastOne(Uri('http://test.eg/#notthere', None))

        conjunction = And(false, true)

        triples = list(self.pack.triples)

        with self.assertRaises(ExtensionError):
            conjunction.run(self.pack)

        self.assertEqual(triples, self.pack.triples)

    def test_and_false_false(self):

        false = AtLeastOne(Uri('http://test.eg/#notthere', None))

        conjunction = And(false, false)

        triples = list(self.pack.triples)

        with self.assertRaises(ExtensionError):
            conjunction.run(self.pack)

        self.assertEqual(triples, self.pack.triples)

    def test_or_true_true(self):

        true = AtLeastOne(Uri('http://example.eg/predicate', None))

        conjunction = Or(true, true)

        triples = list(self.pack.triples)

        conjunction.run(self.pack)

        self.assertEqual(triples, self.pack.triples)

    def test_or_true_false(self):

        true = AtLeastOne(Uri('http://example.eg/predicate', None))
        false = AtLeastOne(Uri('http://test.eg/#notthere', None))

        conjunction = Or(true, false)

        triples = list(self.pack.triples)

        conjunction.run(self.pack)

        self.assertEqual(triples, self.pack.triples)

    def test_or_false_true(self):

        true = AtLeastOne(Uri('http://example.eg/predicate', None))
        false = AtLeastOne(Uri('http://test.eg/#notthere', None))

        conjunction = Or(false, true)

        triples = list(self.pack.triples)

        conjunction.run(self.pack)

        self.assertEqual(triples, self.pack.triples)

    def test_or_false_false(self):

        false = AtLeastOne(Uri('http://test.eg/#notthere', None))

        conjunction = Or(false, false)

        triples = list(self.pack.triples)

        with self.assertRaises(ExtensionError):
            conjunction.run(self.pack)

        self.assertEqual(triples, self.pack.triples)

import unittest
import rdflib

from extensions.triples import TriplePack
from rdfscript.core import (Uri,
                            Value,
                            Name)

from rdfscript.template import (Template,
                                Property,
                                Expansion)
from rdfscript.env import Env

def triple_eval(triple, env):
    (s, p, o) = triple
    s = s.evaluate(env)
    p = p.evaluate(env)
    o = o.evaluate(env)

    return (s, p, o)

class TriplePackTest(unittest.TestCase):

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

        triples =  self.expansion.as_triples(self.env)
        triples = [triple_eval(triple, self.env) for triple in triples]

        bindings = self.env._symbol_table
        templates = self.env._template_table

        self.pack = TriplePack(triples, bindings, templates)

    def testDown(self):
        None

    def test_triples_init(self):

        exp_uri = Name('e').evaluate(self.env)
        triples = [(exp_uri,
                    Value(1),
                    Value(42)),
                   (exp_uri,
                    Uri('http://example.eg/predicate'),
                    Value(2))]

        self.assertEqual(self.pack.triples, triples)
        self.assertEqual(self.pack.bindings, self.env._symbol_table)
        self.assertEqual(self.pack.templates, self.env._template_table)

    def test_triples_lookup(self):

        self.assertEqual(self.pack.lookup(self.v_uri), Value(42))
        self.assertEqual(self.pack.lookup(Uri('http://triplepack.org/#not')), None)

    def test_triples_lookup_template(self):

        self.assertEqual(self.pack.lookup_template(self.template.name.evaluate(self.env)),
                         self.template.as_triples(self.env))
        self.assertEqual(self.pack.lookup_template(Uri('http://triplepack.org/#not')), None)

    def test_triples_get_subjects_1(self):

        self.assertEqual(self.pack.subjects, set([self.expansion.name.evaluate(self.env)]))

    def test_triples_get_subjects_2(self):
        expansion = Expansion(Name('f'),
                              Name('A'),
                              [Value(1),
                               Value(2)],
                              [])

        triples = expansion.as_triples(self.env)
        triples = [triple_eval(triple, self.env) for triple in triples]
        doublePack = TriplePack(self.pack.triples + triples,
                                self.pack.bindings,
                                self.pack.templates)

        self.assertEqual(doublePack.subjects, set([self.expansion.name.evaluate(self.env),
                                                   expansion.name.evaluate(self.env)]))

    def test_triples_get_subjects_empty(self):
        emptyPack = TriplePack([], {}, {})

        self.assertEqual(emptyPack.subjects, set())

    def test_triples_get_predicates(self):

        self.assertEqual(self.pack.predicates, set([Value(1), Uri('http://example.eg/predicate')]))

    def test_triples_get_predicates_empty(self):
        emptyPack = TriplePack([], {}, {})

        self.assertEqual(emptyPack.predicates, set())

    def test_triples_get_objects(self):

        self.assertEqual(self.pack.objects, set([Value(2), Value(42)]))

    def test_triples_get_objects_empty(self):
        emptyPack = TriplePack([], {}, {})

        self.assertEqual(emptyPack.objects, set())

    def test_triples_get_triples_by_subject(self):

        expected_result = [(Name('e').evaluate(self.env),
                            Value(1),
                            Value(42)),
                           (Name('e').evaluate(self.env),
                            Uri('http://example.eg/predicate'),
                            Value(2))]

        self.assertEqual(self.pack.search((Name('e').evaluate(self.env), None, None)),
                         expected_result)

        self.assertEqual(self.pack.search((Name('f').evaluate(self.env), None, None)),
                         [])

    def test_triples_get_triples_by_predicate(self):

        self.assertEqual(self.pack.search((None, Value(1), None)),
                         [(Name('e').evaluate(self.env),
                           Value(1),
                           Value(42))])

        self.assertEqual(self.pack.search((None, Uri('http://example.eg/predicate'), None)),
                         [(Name('e').evaluate(self.env),
                           Uri('http://example.eg/predicate'),
                           Value(2))])

        self.assertEqual(self.pack.search((None, Value(3), None)), [])

    def test_triples_get_triples_by_object(self):

        self.assertEqual(self.pack.search((None, None, Value(42))),
                         [(Name('e').evaluate(self.env),
                           Value(1),
                           Value(42))])

        self.assertEqual(self.pack.search((None, None, Value(2))),
                         [(Name('e').evaluate(self.env),
                           Uri('http://example.eg/predicate'),
                           Value(2))])

        self.assertEqual(self.pack.search((None, None, Value(3))), [])

    def test_triples_get_triples_exact(self):

        self.assertEqual(self.pack.search((Name('e').evaluate(self.env), Value(1), Value(42))),
                         [(Name('e').evaluate(self.env),
                           Value(1),
                           Value(42))])

        self.assertEqual(self.pack.search((Value(1), Value(2, None), Value(3, None))), [])

    def test_triples_get_triples_subject_predicate(self):

        self.assertEqual(self.pack.search((Name('e').evaluate(self.env), Value(1, None), None)),
                         [(Name('e').evaluate(self.env),
                           Value(1, None),
                           Value(42, None))])

        self.assertEqual(self.pack.search((Name('f').evaluate(self.env), Value(1, None), None)), [])
        self.assertEqual(self.pack.search((Name('e').evaluate(self.env), Value(2, None), None)), [])

    def test_triples_get_triples_subject_object(self):

        self.assertEqual(self.pack.search((Name('e').evaluate(self.env), None, Value(42, None))),
                         [(Name('e').evaluate(self.env),
                           Value(1, None),
                           Value(42, None))])

        self.assertEqual(self.pack.search((Name('f').evaluate(self.env), None, Value(42, None))), [])
        self.assertEqual(self.pack.search((Name('e').evaluate(self.env), None, Value(41, None))), [])

    def test_triples_get_triples_predicate_object(self):

        self.assertEqual(self.pack.search((None, Value(1, None), Value(42, None))),
                         [(Name('e').evaluate(self.env),
                           Value(1, None),
                           Value(42, None))])

        self.assertEqual(self.pack.search((None, Value(2, None), Value(42, None))), [])
        self.assertEqual(self.pack.search((None, Value(1, None), Value(41, None))), [])

    def test_triples_subject_has_property(self):

        self.assertTrue(self.pack.has(Name('e').evaluate(self.env), Value(1, None)))
        self.assertFalse(self.pack.has(Name('e').evaluate(self.env), Value(2, None)))
        self.assertFalse(self.pack.has(Name('f').evaluate(self.env), Value(1, None)))

    def test_triples_subject_has_unique_property(self):

        self.assertTrue(self.pack.has_unique(Name('e').evaluate(self.env), Value(1, None)))
        self.assertFalse(self.pack.has_unique(Name('e').evaluate(self.env), Value(2, None)))
        self.assertFalse(self.pack.has_unique(Name('f').evaluate(self.env), Value(1, None)))

        duplicatePack = TriplePack(self.pack.triples + [(Name('e').evaluate(self.env),
                                                         Value(1, None),
                                                         Value(42, None))],
                                   self.pack.bindings,
                                   self.pack.templates)

        self.assertFalse(duplicatePack.has_unique(Name('e').evaluate(self.env), Value(1, None)))

    def test_triples_get_values_for(self):

        self.assertEqual(self.pack.value(Name('e').evaluate(self.env), Value(1, None)),
                         Value(42, None))
        self.assertEqual(self.pack.value(Name('e').evaluate(self.env), Value(2, None)), None)
        self.assertEqual(self.pack.value(Name('f').evaluate(self.env), Value(1, None)), None)

        duplicatePack = TriplePack(self.pack.triples + [(Name('e').evaluate(self.env),
                                                         Value(1, None),
                                                         Value(41, None))],
                                   self.pack.bindings,
                                   self.pack.templates)

        self.assertEqual(duplicatePack.value(Name('e').evaluate(self.env), Value(1, None)),
                         [Value(42, None), Value(41, None)])

    def test_triples_add(self):

        self.assertFalse(self.pack.has(Name('e').evaluate(self.env), Value('fake', None)))
        self.pack.add((Name('e').evaluate(self.env), Value('fake', None), Value('added', None)))
        self.assertTrue(self.pack.has(Name('e').evaluate(self.env), Value('fake', None)))
        self.assertEqual(self.pack.value(Name('e').evaluate(self.env), Value('fake', None)), Value('added', None))

    def test_triples_set(self):

        self.assertEqual(self.pack.value(Name('e').evaluate(self.env), Value(1, None)), Value(42, None))

        self.pack.set(Name('e').evaluate(self.env), Value(1, None), Value('set', None))

        self.assertTrue(self.pack.has_unique(Name('e').evaluate(self.env), Value(1, None)))
        self.assertEqual(self.pack.value(Name('e').evaluate(self.env), Value(1, None)), Value('set', None))

        self.pack.set(Name('e').evaluate(self.env), Value('fake', None), Value('set', None))
        self.assertTrue(self.pack.has(Name('e').evaluate(self.env), Value('fake', None)))

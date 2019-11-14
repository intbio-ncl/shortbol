import unittest

from rdfscript.core import (Name,
                            Value,
                            Uri,
                            Self)
from rdfscript.pragma import ExtensionPragma
from rdfscript.env import Env
from rdfscript.rdfscriptparser import RDFScriptParser

from extensions.cardinality import CardinalityError


class TestExpansionClass(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()
        self.env = Env()
        self.maxDiff = None

    def tearDown(self):
        None

    def test_as_triples(self):

        forms = self.parser.parse('t()(x=12345) e is a t()')
        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)

        expect = [(Name('e'), Name('x').evaluate(self.env), Value(12345))]

        self.assertEqual(expect, e.as_triples(self.env))

    def test_as_triples_with_body(self):

        forms = self.parser.parse('t()(x=12345) e is a t()(y=54321)')
        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)

        expect = [(Name('e'), Name('x').evaluate(self.env), Value(12345)),
                  (Name('e'), Name('y'), Value(54321))]

        self.assertEqual(expect, e.as_triples(self.env))

    def test_as_triples_args(self):

        forms = self.parser.parse('t(x)(<http://predicate.com>=x) e is a t(1)')
        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)

        expect = [(Name('e'), Uri('http://predicate.com'), Value(1))]

        self.assertEqual(expect, e.as_triples(self.env))

    def test_as_triples_args_with_body(self):

        forms = self.parser.parse(
            't(x)(<http://predicate.com>=x) e is a t(1)(x=2)')
        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)

        expect = [(Name('e'), Uri('http://predicate.com'), Value(1)),
                  (Name('e'), Name('x'), Value(2))]

        self.assertEqual(expect, e.as_triples(self.env))

    def test_as_triples_args_with_self(self):

        forms = self.parser.parse('t(x)(self=x) e is a t(1)(x=2)')
        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)

        expect = [(Name('e'), Name('e'), Value(1)),
                  (Name('e'), Name('x'), Value(2))]

        self.assertEqual(expect, e.as_triples(self.env))

    def test_as_triples_with_self_as_object(self):

        forms = self.parser.parse('t()(x=self) e is a t()')
        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)

        expect = [(Name('e'), Name('x').evaluate(self.env), Name('e'))]

        self.assertEqual(expect, e.as_triples(self.env))

    def test_as_triples_args_with_self_prefix(self):

        forms = self.parser.parse('t(x)(self.p=x) e is a t(1)(x=2)')
        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)

        expect = [(Name('e'), Name('e', 'p'), Value(1)),
                  (Name('e'), Name('x'), Value(2))]

        self.assertEqual(expect, e.as_triples(self.env))

    def test_as_triples_with_expansion_in_template(self):

        forms = self.parser.parse('s()(z=true)' +
                                  't()(x = e is a s())' +
                                  'f is a t()')
        s = forms[0]
        t = forms[1]
        f = forms[2]

        s.evaluate(self.env)
        t.evaluate(self.env)

        e = Name('e').evaluate(self.env)
        expect = [(e, Name('z').evaluate(self.env), Value(True)),
                  (Name('f'), Name('x').evaluate(self.env), e)]

        self.assertEqual(expect, f.as_triples(self.env))

    def test_as_triples_with_expansion_in_template_with_self(self):

        forms = self.parser.parse('s()(z=self)' +
                                  't()(x = e is a s())' +
                                  'f is a t()')
        s = forms[0]
        t = forms[1]
        f = forms[2]

        s.evaluate(self.env)
        t.evaluate(self.env)

        expect = [(Name('e').evaluate(self.env),
                   Name('z').evaluate(self.env),
                   Name('e').evaluate(self.env)),
                  (Name('f'),
                   Name('x').evaluate(self.env),
                   Name('e').evaluate(self.env))]

        self.assertEqual(expect, f.as_triples(self.env))

    def test_as_triples_with_context(self):

        forms = self.parser.parse('s()(z=self)' +
                                  'self.f is a s()')

        s = forms[0]
        f = forms[1]

        s.evaluate(self.env)

        self.env.current_self = Uri('e')
        expect = [(Name(Self(), 'f'),
                   Name('z').evaluate(self.env),
                   Name(Self(), 'f'))]

        self.assertEqual(expect, f.as_triples(self.env))

    def test_as_triples_with_self_named_expansion_in_template(self):

        forms = self.parser.parse('s()(z=self)' +
                                  't()(x=self.e is a s())' +
                                  'f is a t()')
        s = forms[0]
        t = forms[1]
        f = forms[2]

        s.evaluate(self.env)
        t.evaluate(self.env)

        expect = [(Name('f', 'e'),
                   Name('z').evaluate(self.env),
                   Name('f', 'e')),
                  (Name('f'),
                   Name('x').evaluate(self.env),
                   Name('f', 'e'))]

        self.assertEqual(expect, f.as_triples(self.env))

    def test_extensions_argument_binding(self):

        forms = self.parser.parse('t(a)(@extension AtLeastOne(a))' +
                                  'e is a t("a")')

        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)
        ext = ExtensionPragma('AtLeastOne', [Value("a")])
        self.assertEqual(e.get_extensions(self.env), [ext])

    def test_extensions_multiple_argument_binding(self):

        forms = self.parser.parse('t(a, b)(@extension ext(a, b))' +
                                  'e is a t(1, 2)')

        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)
        ext = ExtensionPragma('ext', [Value(1), Value(2)])
        self.assertEqual(e.get_extensions(self.env), [ext])

    def test_extensions_mixed_argument_binding(self):

        forms = self.parser.parse('t(a)(@extension ext(12345, a))' +
                                  'e is a t(1)')

        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)
        ext = ExtensionPragma('ext', [Value(12345), Value(1)])
        self.assertEqual(e.get_extensions(self.env), [ext])

    def test_extensions_from_multiple_templates(self):

        forms = self.parser.parse('s(a)(@extension ext(a))' +
                                  't(a)(s("s") @extension ext(a))' +
                                  'e is a t("t")')

        s = forms[0]
        t = forms[1]
        e = forms[2]

        s.evaluate(self.env)
        t.evaluate(self.env)
        exts = [ExtensionPragma('ext', [Value("s")]),
                ExtensionPragma('ext', [Value("t")])]

        self.assertEqual(e.get_extensions(self.env), exts)

    def test_extensions_self_in_extension_arguments(self):

        forms = self.parser.parse('s()(@extension ext(self.name))' +
                                  't()(s() @extension ext(self.name))' +
                                  'e is a t()')

        s = forms[0]
        t = forms[1]
        e = forms[2]

        s.evaluate(self.env)
        t.evaluate(self.env)
        exts = [ExtensionPragma('ext', [Name(Self(), 'name')]),
                ExtensionPragma('ext', [Name(Self(), 'name')])]

        self.assertEqual(e.get_extensions(self.env), exts)

    def test_extensions_in_expansion(self):

        forms = self.parser.parse('s(a)(@extension ext(a))' +
                                  't(a)(s("s") @extension ext(a))' +
                                  'e is a t("t")(@extension ext("e"))')

        s = forms[0]
        t = forms[1]
        e = forms[2]

        s.evaluate(self.env)
        t.evaluate(self.env)

        exts = [ExtensionPragma('ext', [Value("s")]),
                ExtensionPragma('ext', [Value("t")]),
                ExtensionPragma('ext', [Value("e")])]

        self.assertEqual(e.get_extensions(self.env), exts)

    def test_evaluate_runs_extensions_with_error(self):

        forms = self.parser.parse('t(a)(@extension AtLeastOne(a))' +
                                  'e is a t(property)()')

        t = forms[0]
        e = forms[1]

        graph_triples = list(self.env._rdf._g.triples((None, None, None)))
        self.assertEqual(len(graph_triples), 0)

        t.evaluate(self.env)
        with self.assertRaises(CardinalityError):
            e.evaluate(self.env)

        graph_triples = list(self.env._rdf._g.triples((None, None, None)))
        self.assertEqual(len(graph_triples), 0)

    def test_evaluate_runs_extensions(self):

        forms = self.parser.parse('t(a)(@extension AtLeastOne(a))' +
                                  'e is a t(property)(property=12345)')

        t = forms[0]
        e = forms[1]

        graph_triples = list(self.env._rdf._g.triples((None, None, None)))
        self.assertEqual(len(graph_triples), 0)

        t.evaluate(self.env)
        e.evaluate(self.env)

        graph_triples = list(self.env._rdf._g.triples((None, None, None)))
        self.assertEqual(len(graph_triples), 1)

    def test_add_object_for_inherited_predicate(self):

        forms = self.parser.parse('t()(x = 1)' +
                                  'e is a t()(x = 2)')

        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)

        expect = [(Name('e'),
                   Name('x').evaluate(self.env),
                   Value(1)),
                  (Name('e'),
                   Name('x'),
                   Value(2))]

        self.assertEqual(expect, e.as_triples(self.env))

    def test_bodied_expansion_in_template(self):

        forms = self.parser.parse('s()(a = 1)' +
                                  't()(x = self.e is a s()(b = 2))' +
                                  'f is a t()')

        s = forms[0]
        t = forms[1]
        f = forms[2]

        s.evaluate(self.env)
        t.evaluate(self.env)

        expect = [(Name('f', 'e'),
                   Name('a').evaluate(self.env),
                   Value(1)),
                  (Name('f', 'e'),
                   Name('b').evaluate(self.env),
                   Value(2)),
                  (Name('f'),
                   Name('x').evaluate(self.env),
                   Name('f', 'e'))]

        self.assertEqual(expect, f.as_triples(self.env))

    def test_as_triples_multiple_inheritance(self):

        forms = self.parser.parse('s()(a=123)' +
                                  't()(b=456)' +
                                  'u()(s() t())' +
                                  'e is a u()')

        s = forms[0]
        t = forms[1]
        u = forms[2]
        e = forms[3]

        s.evaluate(self.env)
        t.evaluate(self.env)
        u.evaluate(self.env)

        expect = [(Name('e'),
                   Name('a').evaluate(self.env),
                   Value(123)),
                  (Name('e'),
                   Name('b').evaluate(self.env),
                   Value(456))]

        self.assertEqual(expect, e.as_triples(self.env))

    def test_similar_args_treated_as_unique(self):

        forms = self.parser.parse('s(x, y)(a = x b = y)' +
                                  'e is a s(1, 1)')

        s = forms[0]
        e = forms[1]

        s.evaluate(self.env)

        expect = [(Name('e'), Name('a').evaluate(self.env), Value(1)),
                  (Name('e'), Name('b').evaluate(self.env), Value(1))]

        self.assertEqual(expect, e.as_triples(self.env))

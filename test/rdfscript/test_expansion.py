import unittest
import pdb

import sys
import os

sys.path.insert(1, os.path.join(sys.path[0], '..', ".."))

from rdfscript.core import Name
from rdfscript.core import Value
from rdfscript.core import Uri
from rdfscript.core import Self
from rdfscript.core import Identifier
from rdfscript.pragma import ExtensionPragma
from rdfscript.env import Env
from rdfscript.parser import Parser

from extensions.cardinality import CardinalityError


class TestExpansionClass(unittest.TestCase):

    def setUp(self):
        self.parser = Parser()
        self.env = Env()
        self.maxDiff = None

    def tearDown(self):
        None

    def test_as_triples(self):
        forms = self.parser.parse('t()(x=12345) e is a t()')
        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)
        expect = [(Identifier(Name('e')),
                   Identifier(Name('x')).evaluate(self.env),
                   Value(12345))]

        self.assertCountEqual(expect, e.as_triples(self.env))

    def test_as_triples_with_body(self):
        forms = self.parser.parse('t()(x=12345) e is a t()(y=54321)')
        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)

        expect = [(Identifier(Name('e')),
                   Identifier(Name('x')).evaluate(self.env),
                   Value(12345)),
                  (Identifier(Name('e')),
                   Identifier(Name('y')),
                   Value(54321))]

        self.assertCountEqual(expect, e.as_triples(self.env))

    def test_as_triples_args(self):
        forms = self.parser.parse('t(x)(<http://predicate.com>=x) e is a t(1)')
        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)

        expect = [(Identifier(Name('e')),
                   Uri('http://predicate.com'),
                   Value(1))]

        self.assertCountEqual(expect, e.as_triples(self.env))

    def test_as_triples_args_with_body(self):

        forms = self.parser.parse(
            't(x)(<http://predicate.com>=x) e is a t(1)(x=2)')
        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)

        expect = [(Identifier(Name('e')), Uri('http://predicate.com'), Value(1)),
                  (Identifier(Name('e')), Identifier(Name('x')), Value(2))]

        self.assertCountEqual(expect, e.as_triples(self.env))

    def test_as_triples_args_with_self(self):
        forms = self.parser.parse('t(x)(self=x) e is a t(1)(x=2)')
        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)

        expect = [(Identifier(Name('e')), Identifier(Name('e')), Value(1)),
                  (Identifier(Name('e')), Identifier(Name('x')), Value(2))]

        self.assertCountEqual(expect, e.as_triples(self.env))

    def test_as_triples_with_self_as_object(self):
        forms = self.parser.parse('t()(x=self) e is a t()')
        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)

        expect = [(Identifier(Name('e')),
                   Identifier(Name('x')).evaluate(self.env),
                   Identifier(Name('e')))]

        self.assertCountEqual(expect, e.as_triples(self.env))

    def test_as_triples_args_with_self_prefix(self):
        forms = self.parser.parse('t(x)(self.p=x) e is a t(1)(x=2)')
        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)

        expect = [(Identifier(Name('e')),
                   Identifier(Name('e'), Name('p')),
                   Value(1)),
                  (Identifier(Name('e')),
                   Identifier(Name('x')),
                   Value(2))]

        print(type(e.as_triples(self.env)))
        for k in  e.as_triples(self.env):
            print(k)
        print("\n\n")
        for k in  e.as_triples(self.env):
            print(k)
        print("\n\n")
        for k in  e.as_triples(self.env):
            print(k)
            
        self.assertCountEqual(expect,e.as_triples(self.env))
        self.assertCountEqual(expect, e.as_triples(self.env))


    def test_as_triples_with_expansion_in_template(self):
        forms = self.parser.parse('s()(z=true)' +
                                  't()(x = e is a s())' +
                                  'f is a t()')
        s = forms[0]
        t = forms[1]
        f = forms[2]

        s.evaluate(self.env)
        t.evaluate(self.env)

        e = Identifier(Name('e')).evaluate(self.env)
        expect = [(e,
                   Identifier(Name('z')).evaluate(self.env),
                   Value(True)),
                  (Identifier(Name('f')),
                   Identifier(Name('x')).evaluate(self.env),
                   e)]

        self.assertCountEqual(expect, f.as_triples(self.env))

    def test_as_triples_with_expansion_in_template_with_self(self):
        forms = self.parser.parse('s()(z=self)' +
                                  't()(x = e is a s())' +
                                  'f is a t()')
        s = forms[0]
        t = forms[1]
        f = forms[2]

        s.evaluate(self.env)
        t.evaluate(self.env)

        expect = [(Identifier(Name('e')).evaluate(self.env),
                   Identifier(Name('z')).evaluate(self.env),
                   Identifier(Name('e')).evaluate(self.env)),
                  (Identifier(Name('f')),
                   Identifier(Name('x')).evaluate(self.env),
                   Identifier(Name('e')).evaluate(self.env))]

        self.assertCountEqual(expect, f.as_triples(self.env))


    def test_as_triples_with_self_named_expansion_in_template(self):
        forms = self.parser.parse('s()(z=self)' +
                                  't()(x=self.e is a s())' +
                                  'f is a t()')
        s = forms[0]
        t = forms[1]
        f = forms[2]

        s.evaluate(self.env)
        t.evaluate(self.env)

        expect = [(Identifier(*map(Name, ['f', 'e'])),
                   Identifier(Name('z')).evaluate(self.env),
                   Identifier(*map(Name, ['f', 'e']))),
                  (Identifier(Name('f')),
                   Identifier(Name('x')).evaluate(self.env),
                   Identifier(*map(Name, ['f', 'e'])))]

        self.assertCountEqual(expect, f.as_triples(self.env))

    def test_extensions_argument_binding(self):

        forms = self.parser.parse('t(a)(@extension AtLeastOne(a))' +
                                  'e is a t("a")')

        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)
        ext = ExtensionPragma('AtLeastOne', [Value("a")])
        self.assertCountEqual(e.get_extensions(self.env), [ext])

    def test_extensions_multiple_argument_binding(self):

        forms = self.parser.parse('t(a, b)(@extension ext(a, b))' +
                                  'e is a t(1, 2)')

        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)
        ext = ExtensionPragma('ext', [Value(1), Value(2)])
        self.assertCountEqual(e.get_extensions(self.env), [ext])

    def test_extensions_mixed_argument_binding(self):

        forms = self.parser.parse('t(a)(@extension ext(12345, a))' +
                                  'e is a t(1)')

        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)
        ext = ExtensionPragma('ext', [Value(12345), Value(1)])
        self.assertCountEqual(e.get_extensions(self.env), [ext])

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

        self.assertCountEqual(e.get_extensions(self.env), exts)

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

        self.assertCountEqual(e.get_extensions(self.env), exts)

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

        self.assertCountEqual(e.get_extensions(self.env), exts)

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
        
        expect = [(Identifier(Name('e')),
                   Identifier(Name('x')).evaluate(self.env),
                   Value(1)),
                  (Identifier(Name('e')),
                   Identifier(Name('x')),
                   Value(2))]

        self.assertCountEqual(expect, e.as_triples(self.env))

    def test_bodied_expansion_in_template(self):
        forms = self.parser.parse('s()(a = 1)' +
                                  't()(x = self.e is a s()(b = 2))' +
                                  'f is a t()')

        s = forms[0]
        t = forms[1]
        f = forms[2]

        s.evaluate(self.env)
        t.evaluate(self.env)

        expect = [(Identifier(Name('f'), Name('e')),
                   Identifier(Name('a')).evaluate(self.env),
                   Value(1)),
                  (Identifier(Name('f'), Name('e')),
                   Identifier(Name('b')).evaluate(self.env),
                   Value(2)),
                  (Identifier(Name('f')),
                   Identifier(Name('x')).evaluate(self.env),
                   Identifier(Name('f'), Name('e')))]

        self.assertCountEqual(expect, f.as_triples(self.env))

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

        self.assertCountEqual(expect, e.as_triples(self.env))

    def test_similar_args_treated_as_unique(self):

        forms = self.parser.parse('s(x, y)(a = x b = y)' +
                                  'e is a s(1, 1)')

        s = forms[0]
        e = forms[1]

        s.evaluate(self.env)

        expect = [(Name('e'), Name('a').evaluate(self.env), Value(1)),
                  (Name('e'), Name('b').evaluate(self.env), Value(1))]

        self.assertCountEqual(expect, e.as_triples(self.env))

    '''
    as_triples regression tests.
    '''
    def test_as_triples_multiple_runs(self):
        forms = self.parser.parse('t(x)(self.p=x) e is a t(1)(x=2)')
        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)
        e.evaluate(self.env)

        e_iter_1_triples = e.as_triples(self.env)
        e_iter_2_triples = e.as_triples(self.env)

        t_iter_1_triples = e.as_triples(self.env)
        t_iter_2_triples = e.as_triples(self.env)

        self.assertCountEqual(e_iter_1_triples, e_iter_2_triples)
        self.assertCountEqual(t_iter_1_triples, t_iter_2_triples)


    def test_as_triples_multiple_runs_multiple_inheritence(self):

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
        e.evaluate(self.env)


        s_iter_1_triples = s.as_triples(self.env)
        s_iter_2_triples = s.as_triples(self.env)

        t_iter_1_triples = t.as_triples(self.env)
        t_iter_2_triples = t.as_triples(self.env)

        u_iter_1_triples = u.as_triples(self.env)
        u_iter_2_triples = u.as_triples(self.env)

        e_iter_1_triples = e.as_triples(self.env)
        e_iter_2_triples = e.as_triples(self.env)


        self.assertCountEqual(s_iter_1_triples,s_iter_2_triples)
        self.assertCountEqual(t_iter_1_triples,t_iter_2_triples)
        self.assertCountEqual(u_iter_1_triples,u_iter_2_triples)
        self.assertCountEqual(e_iter_1_triples,e_iter_2_triples)


    def test_as_triples_multiple_runs_extensions_self_in_extension_arguments(self):
        forms = self.parser.parse('s()(@extension ext(self.name))' +
                            't()(s() @extension ext(self.name))' +
                            'e is a t()')

        s = forms[0]
        t = forms[1]
        e = forms[2]

        s.evaluate(self.env)
        t.evaluate(self.env)


        s_iter_1_triples = s.as_triples(self.env)
        s_iter_2_triples = s.as_triples(self.env)

        t_iter_1_triples = t.as_triples(self.env)
        t_iter_2_triples = t.as_triples(self.env)


        self.assertCountEqual(s_iter_1_triples,s_iter_2_triples)
        self.assertCountEqual(t_iter_1_triples,t_iter_2_triples)





import unittest

import sys
import os

sys.path.insert(1, os.path.join(sys.path[0], '..', ".."))

from rdfscript.env import Env
from rdfscript.parser import Parser
from rdfscript.core import Name, Uri, Self, Value, Parameter, Identifier

from rdfscript.template import Template

from rdfscript.pragma import ExtensionPragma


class TemplateClassTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()
        self.parser = Parser()
        self.maxDiff = None

    def tearDown(self):
        None

    def test_init(self):
        '''
        Simplest check, does Templates Identifier get added to parts list.
        '''
        template = Template(Identifier(Name('x')), [], [])
        self.assertEqual(template.identifier.parts[0], Name('x'))

    def test_as_triples_empty(self):
        '''
        Tests if triples list is empty when no parser call.
        '''
        template = Template(Identifier(Name('x')), [], [])
        self.assertCountEqual(template.as_triples(self.env), [])

    def test_as_triples_simple_triple(self):
        '''
        Tests if triples list is not empty when parser call.
        '''
        template = self.parser.parse('t()(x = z)')[0]
        expect = [(Identifier(Self()), Identifier(Name('x')), Identifier(Name('z')))]
        self.assertCountEqual(template.as_triples(self.env), expect)

    def test_as_triples_simple_triple_with_self(self):
        '''
        Tests if triples list is not empty when parser call with self.
        '''
        template = self.parser.parse('t()(x = self)')[0]
        expect = [(Identifier(Self()), Identifier(Name('x')), Identifier(Self()))]
        self.assertCountEqual(template.as_triples(self.env), expect)

    def test_as_triples_multiple_properties(self):
        '''
        Tests if triples list is not empty when parser call with multiple properties.
        '''
        template = self.parser.parse('t()(x = y z = 12345)')[0]
        expect = [(Identifier(Self()), Identifier(Name('x')), Identifier(Name('y'))),
                  (Identifier(Self()), Identifier(Name('z')), Value(12345))]
        self.assertCountEqual(template.as_triples(self.env), expect)

    def test_as_triples_with_base(self):
        '''
        Test for correctness when a base and specialised template are defined
        '''
        forms = self.parser.parse('a()(x = 1) b()(a() y = 2)')
        base = forms[0]
        specialised = forms[1]
        base.evaluate(self.env)

        expect = [(Identifier(Self()), Identifier(Name('x')).evaluate(self.env), Value(1)),
                  (Identifier(Self()), Identifier(Name('y')), Value(2))]

        self.assertCountEqual(specialised.as_triples(self.env), expect)

    def test_as_triples_with_base_chain(self):
        '''
        Test for correctness when a base and multiple/chained specialised templates are defined
        # Calls Expansion() ??
        '''

        forms = self.parser.parse('a()(x = 1)' +
                                  'b()(a() y = 2)' +
                                  'c()(b() z = 3)')
        a = forms[0]
        b = forms[1]
        c = forms[2]

        a.evaluate(self.env)
        b.evaluate(self.env)

        expect = [(Identifier(Self()), Identifier(Name('x')).evaluate(self.env), Value(1)),
                  (Identifier(Self()), Identifier(Name('y')).evaluate(self.env), Value(2)),
                  (Identifier(Self()), Identifier(Name('z')), Value(3))]

        self.assertCountEqual(c.as_triples(self.env), expect)

    def test_as_triples_with_base_with_self(self):
        '''
        Test for correctness when a base and specialised templates are defined
        and base has self as property.
        '''
        forms = self.parser.parse('a()(x = self) b()(a() y = 2)')
        base = forms[0]
        specialised = forms[1]
        base.evaluate(self.env)

        expect = [(Identifier(Self()), Identifier(Name('x')).evaluate(self.env), Identifier(Self())),
                  (Identifier(Self()), Identifier(Name('y')), Value(2))]

        self.assertCountEqual(specialised.as_triples(self.env), expect)
    
    def test_as_triples_params(self):
        '''
        Test for correctness when a template is defined with param and set to property
        '''
        forms = self.parser.parse('a(x)(property = x)')
        a = forms[0]
        expect = [(Identifier(Self()), Identifier(Name('property')), Identifier(Parameter('x',0)))]

        for index,triple in enumerate(a.as_triples(self.env)):
            for tuple_index,element in enumerate(triple):
                self.assertEqual(element,expect[index][tuple_index])
        self.assertCountEqual(a.as_triples(self.env), expect)

    def test_as_triples_with_base_with_params(self):
        '''
        Test for correctness when a template is defined and property is set to value.
        '''
        forms = self.parser.parse('a(x)(x = 12345) b(y)(a(y))')
        a = forms[0]
        b = forms[1]
        template_name = a.identifier.evaluate(self.env)

        self.env.assign_template(template_name, a.as_triples(self.env))
        expect = [(Identifier(Self()), Identifier(Parameter('y', 0)), Value(12345))]
                
        self.assertCountEqual(expect, b.as_triples(self.env))

    def test_as_triples_with_base_with_args(self):
        '''
        Test for correctness when a template is defined and property is set to value.
        And specialised template contains arg
        '''

        forms = self.parser.parse('a(x)(x = 12345) b()(a(12345))')
        a = forms[0]
        b = forms[1]

        a.evaluate(self.env)
        expect = [(Identifier(Self()), Value(12345), Value(12345))]

        self.assertCountEqual(expect, b.as_triples(self.env))

    def test_as_triples_multiple_base_args_and_parameters(self):

        forms = self.parser.parse('a(x, y)(x = y)' +
                                  'b(x, y)(a(x, "string") z=y)' +
                                  'c(x, y)(b(1, 2) x=y)')
        a = forms[0]
        b = forms[1]
        c = forms[2]

        a.evaluate(self.env)
        b.evaluate(self.env)

        expect = [(Identifier(Self()), Value(1), Value("string")),
                  (Identifier(Self()), Identifier(Name('z')).evaluate(self.env), Value(2)),
                  (Identifier(Self()), Identifier(Parameter('x', 0)), Identifier(Parameter('y', 0)))]

        self.assertCountEqual(expect, c.as_triples(self.env))

    @unittest.skip("There is no longer a current_self")
    def test_current_self_preserved(self):
        forms = self.parser.parse('a(x, y, z)(self=self)')
        a = forms[0]

        previous_self = self.env.uri
        a.as_triples(self.env)
        new_self = self.env.current_self
        self.assertEqual(previous_self, new_self)

    def test_as_triples_with_expansion_in_property(self):
        forms = self.parser.parse('a()(x = 1) b()(y = e is a a())')
        a = forms[0]
        b = forms[1]

        a.evaluate(self.env)

        expect = [(Identifier(Name('e')), Identifier(Name('x')).evaluate(self.env), Value(1)),
                  (Identifier(Self()), Identifier(Name('y')), Identifier(Name('e')))]

        self.assertCountEqual(expect, b.as_triples(self.env))

    def test_as_triples_with_expansion_in_property_with_self(self):
        forms = self.parser.parse('a()(x = 1) b()(self.y = e is a a())')
        a = forms[0]
        b = forms[1]

        a.evaluate(self.env)

        expect = [(Identifier(Name('e')), Identifier(Name('x')).evaluate(self.env), Value(1)),
                  (Identifier(Self()), Identifier(Self(), Name('y')), Identifier(Name('e')))]

        self.assertCountEqual(expect, b.as_triples(self.env))

    def test_as_triples_with_expansion_in_property_with_self_as_name(self):
        forms = self.parser.parse('a()(x = 1) b()(y = self.e is a a())')
        a = forms[0]
        b = forms[1]

        a.evaluate(self.env)

        expect = [(Identifier(Self(), Name('e')), Identifier(Name('x')).evaluate(self.env), Value(1)),
                  (Identifier(Self()), Identifier(Name('y')), Identifier(Self(), Name('e')))]

        self.assertCountEqual(expect, b.as_triples(self.env))

    def test_as_triples_with_base_with_self_named_expansion(self):
        forms = self.parser.parse('s()(z=self) t()(x=self.e is a s())')
        s = forms[0]
        t = forms[1]
        
        s.evaluate(self.env)

        e = Identifier(Self(), Name('e'))

        expect_s = [(Identifier(Self()), Identifier(Name('z')), Identifier(Self()))]
        self.assertCountEqual(expect_s, s.as_triples(self.env))

        expect_t = [(e, Identifier(Name('z')).evaluate(self.env), e),
                   (Identifier(Self()), Identifier(Name('x')), e)]
        self.assertCountEqual(expect_t, t.as_triples(self.env))

    def test_as_triples_with_expansion_as_argument(self):
        forms = self.parser.parse('r()(y=1) s(exp)(x=exp)' +
                                  't()(s(e is a r()))')

        r = forms[0]
        s = forms[1]
        t = forms[2]

        r.evaluate(self.env)
        s.evaluate(self.env)

        e = self.parser.parse('e is a r()')[0]

        expect = [(Identifier(Self()), Identifier(Name('x')).evaluate(self.env), e)]

        self.assertCountEqual(expect, t.as_triples(self.env))

    def test_evaluate_stores_triples(self):
        forms = self.parser.parse('t()(x=1 y=2)')
        t = forms[0]

        self.assertFalse(self.env.lookup_template(t.identifier.evaluate(self.env)))

        t.evaluate(self.env)

        found = self.env.lookup_template(t.identifier.evaluate(self.env))
        expect = [(Identifier(Self()), Identifier(Name('x')).evaluate(self.env), Value(1)),
                  (Identifier(Self()), Identifier(Name('y')).evaluate(self.env), Value(2))]

        self.assertCountEqual(found, expect)

    def test_evaluate_stores_triples_of_base(self):
        forms = self.parser.parse('s()(z=3)t()(x=1 y=2 s())')
        s = forms[0]
        t = forms[1]

        self.assertFalse(self.env.lookup_template(t.identifier.evaluate(self.env)))

        s.evaluate(self.env)
        t.evaluate(self.env)

        found = self.env.lookup_template(t.identifier.evaluate(self.env))
        expect = [(Identifier(Self()), Identifier(Name('x')).evaluate(self.env), Value(1)),
                  (Identifier(Self()), Identifier(Name('y')).evaluate(self.env), Value(2)),
                  (Identifier(Self()), Identifier(Name('z')).evaluate(self.env), Value(3))]

        self.assertCountEqual(found, expect)

    def test_evaluate_stores_triples_of_bases(self):
        forms = self.parser.parse('q()(a=4) s()(z=3)t()(x=1 y=2 s() q())')
        q = forms[0]
        s = forms[1]
        t = forms[2]

        self.assertFalse(self.env.lookup_template(t.identifier.evaluate(self.env)))

        q.evaluate(self.env)
        s.evaluate(self.env)
        t.evaluate(self.env)

        found = self.env.lookup_template(t.identifier.evaluate(self.env))
        expect = [(Identifier(Self()), Identifier(Name('x')).evaluate(self.env), Value(1)),
                  (Identifier(Self()), Identifier(Name('y')).evaluate(self.env), Value(2)),
                  (Identifier(Self()), Identifier(Name('z')).evaluate(self.env), Value(3)),
                  (Identifier(Self()), Identifier(Name('a')).evaluate(self.env), Value(4))]

        self.assertCountEqual(found, expect)

    def test_evaluate_stores_triples_of_chained_bases(self):
        forms = self.parser.parse('q()(a=4) s()(z=3 q())t()(x=1 y=2 s())')
        q = forms[0]
        s = forms[1]
        t = forms[2]

        self.assertFalse(self.env.lookup_template(t.identifier.evaluate(self.env)))

        q.evaluate(self.env)
        s.evaluate(self.env)
        t.evaluate(self.env)

        found = self.env.lookup_template(t.identifier.evaluate(self.env))
        expect = [(Identifier(Self()), Identifier(Name('x')).evaluate(self.env), Value(1)),
                  (Identifier(Self()), Identifier(Name('y')).evaluate(self.env), Value(2)),
                  (Identifier(Self()), Identifier(Name('z')).evaluate(self.env), Value(3)),
                  (Identifier(Self()), Identifier(Name('a')).evaluate(self.env), Value(4))]

        self.assertCountEqual(found, expect)

    def test_evaluate_stores_triples_with_parameterised_bases(self):
        forms = self.parser.parse('q(p)(a=p)' +
                                  's(t)(z=t q("s"))' +
                                  't()(x=1 y=2 s("t"))')
        q = forms[0]
        s = forms[1]
        t = forms[2]

        self.assertFalse(self.env.lookup_template(t.identifier.evaluate(self.env)))

        q.evaluate(self.env)
        s.evaluate(self.env)
        t.evaluate(self.env)

        found = self.env.lookup_template(t.identifier.evaluate(self.env))
        expect = [(Identifier(Self()), Identifier(Name('x')).evaluate(self.env), Value(1)),
                  (Identifier(Self()), Identifier(Name('y')).evaluate(self.env), Value(2)),
                  (Identifier(Self()), Identifier(Name('z')).evaluate(self.env), Value("t")),
                  (Identifier(Self()), Identifier(Name('a')).evaluate(self.env), Value("s"))]

        self.assertCountEqual(found, expect)

    def test_evaluate_stores_triples_with_forward_parameterised_bases(self):
        forms = self.parser.parse('q(p)(a=p)' +
                                  's(t)(z=t q(t))' +
                                  't()(x=1 y=2 s("t"))')
        q = forms[0]
        s = forms[1]
        t = forms[2]

        self.assertFalse(self.env.lookup_template(t.identifier.evaluate(self.env)))

        q.evaluate(self.env)
        s.evaluate(self.env)
        t.evaluate(self.env)

        found = self.env.lookup_template(t.identifier.evaluate(self.env))
        expect = [(Identifier(Self()), Identifier(Name('x')).evaluate(self.env), Value(1)),
                  (Identifier(Self()), Identifier(Name('y')).evaluate(self.env), Value(2)),
                  (Identifier(Self()), Identifier(Name('z')).evaluate(self.env), Value("t")),
                  (Identifier(Self()), Identifier(Name('a')).evaluate(self.env), Value("t"))]

        self.assertCountEqual(found, expect)

    def test_evaluate_stores_triples_with_unevaluated_parameter(self):
        forms = self.parser.parse('q(p)(a=p)' +
                                  's(t)(z=t q(t))' +
                                  't(t)(x=1 y=2 s(t))')
        q = forms[0]
        s = forms[1]
        t = forms[2]

        self.assertFalse(self.env.lookup_template(t.identifier.evaluate(self.env)))

        q.evaluate(self.env)
        s.evaluate(self.env)
        t.evaluate(self.env)

        param = Identifier(Parameter('t', 0))

        found = self.env.lookup_template(t.identifier.evaluate(self.env))
        expect = [(Identifier(Self()), Identifier(Name('x')).evaluate(self.env), Value(1)),
                  (Identifier(Self()), Identifier(Name('y')).evaluate(self.env), Value(2)),
                  (Identifier(Self()), Identifier(Name('z')).evaluate(self.env), param),
                  (Identifier(Self()), Identifier(Name('a')).evaluate(self.env), param)]

        self.assertCountEqual(found, expect)

    def test_evaluate_stores_triples_with_unevaluated_parameters(self):
        forms = self.parser.parse('q(p)(a=p)' +
                                  's(u,v)(z=u q(v))' +
                                  't(a,b)(x=1 y=2 s(a,b))')
        q = forms[0]
        s = forms[1]
        t = forms[2]

        self.assertFalse(self.env.lookup_template(t.identifier.evaluate(self.env)))

        q.evaluate(self.env)
        s.evaluate(self.env)
        t.evaluate(self.env)

        a = Identifier(Parameter('a', 0))
        b = Identifier(Parameter('b', 1))

        found = self.env.lookup_template(t.identifier.evaluate(self.env))
        expect = [(Identifier(Self()), Identifier(Name('x')).evaluate(self.env), Value(1)),
                  (Identifier(Self()), Identifier(Name('y')).evaluate(self.env), Value(2)),
                  (Identifier(Self()), Identifier(Name('z')).evaluate(self.env), a),
                  (Identifier(Self()), Identifier(Name('a')).evaluate(self.env), b)]

        self.assertCountEqual(found, expect)

    def test_evaluate_stores_triples_with_expansion_as_property(self):
        forms = self.parser.parse('a(x)(p=x)' +
                                  'b()(q = e is a a(2))')

        a = forms[0]
        b = forms[1]

        a.evaluate(self.env)
        b.evaluate(self.env)

        env = self.env
        me = Identifier(Self())

        found = env.lookup_template(b.identifier.evaluate(env))
        expect = [(Identifier(Name('e')).evaluate(env), Identifier(Name('p')).evaluate(env), Value(2)),
                  (me, Identifier(Name('q')).evaluate(env), Identifier(Name('e')).evaluate(env))]

        self.assertCountEqual(found, expect)

    def test_evaluate_stores_triples_with_expansion_in_body(self):
        forms = self.parser.parse('a(x)(p=x)' +
                                  'b()(e is a a(2))')

        a = forms[0]
        b = forms[1]

        a.evaluate(self.env)
        b.evaluate(self.env)

        env = self.env

        found = env.lookup_template(b.identifier.evaluate(env))
        expect = [(Identifier(Name('e')).evaluate(env), Identifier(Name('p')).evaluate(env), Value(2))]

        self.assertCountEqual(found, expect)

    def test_evaluate_stores_triples_with_expansion_in_argument(self):
        forms = self.parser.parse('a(x)(p=x)' +
                                  'b(x)(e=x)' +
                                  'c()(b(f is a a(2)))')

        a = forms[0]
        b = forms[1]
        c = forms[2]

        a.evaluate(self.env)
        b.evaluate(self.env)
        c.evaluate(self.env)

        env = self.env
        me = Identifier(Self())

        found = env.lookup_template(c.identifier.evaluate(env))
        expect = [(me, Identifier(Name('e')).evaluate(env), Identifier(Name('f')).evaluate(env))]
        
        self.assertCountEqual(found, expect)

        expect = [(Identifier(Name('f')).evaluate(env), Identifier(Name('p')).evaluate(env), Value(2))]
        self.assertCountEqual(self.env._rdf.triples, expect)

    def test_evaluate_stores_triples_with_expansions(self):
        forms = self.parser.parse('a(x)(e=x)' +
                                  'b(y)(p=y)' +
                                  'c()(a(f is a b(1))' +
                                  '    q = g is a b(2)'  +
                                  '    h is a b(3))')

        a = forms[0]
        b = forms[1]
        c = forms[2]

        a.evaluate(self.env)
        b.evaluate(self.env)
        c.evaluate(self.env)

        me = Identifier(Self())
        env = self.env

        f = Identifier(Name('f')).evaluate(env)
        g = Identifier(Name('g')).evaluate(env)
        h = Identifier(Name('h')).evaluate(env)

        found = env.lookup_template(c.identifier.evaluate(env))
        expect = [(me, Identifier(Name('e')).evaluate(env), f),
                  (g, Identifier(Name('p')).evaluate(env), Value(2)),
                  (me, Identifier(Name('q')).evaluate(env), g),
                  (h, Identifier(Name('p')).evaluate(env), Value(3))]

        self.assertCountEqual(found, expect)

        expect = [(f, Identifier(Name('p')).evaluate(env), Value(1))]
        self.assertCountEqual(self.env._rdf.triples, expect)

    def test_init_extensions(self):
        forms = self.parser.parse('t()(@extension E() @extension F())')
        t = forms[0]

        expect = [ExtensionPragma('E', []), ExtensionPragma('F', [])]

        self.assertCountEqual(t.collect_extensions(self.env), expect)

    def test_evaluate_stores_extensions(self):
        forms = self.parser.parse('t()(@extension E() @extension F())')
        t = forms[0]

        t.evaluate(self.env)

        found = self.env.lookup_extensions(t.identifier.evaluate(self.env))

        self.assertCountEqual(found, [ExtensionPragma(
            'E', []), ExtensionPragma('F', [])])

    def test_evaluate_stores_base_extensions(self):
        forms = self.parser.parse(
            's()(@extension F()) t()(s() @extension E())')
        s = forms[0]
        t = forms[1]

        s.evaluate(self.env)
        t.evaluate(self.env)

        found = self.env.lookup_extensions(t.identifier.evaluate(self.env))
        expect = [ExtensionPragma('F', []), ExtensionPragma('E', [])]

        self.assertCountEqual(found, expect)

    def test_evaluate_extension_arguments(self):
        forms = self.parser.parse('t()(@extension E(12345))')
        t = forms[0]

        t.evaluate(self.env)

        found = self.env.lookup_extensions(t.identifier.evaluate(self.env))

        self.assertCountEqual(found, [ExtensionPragma('E', [Value(12345)])])

    def test_evaluate_extension_arguments_name(self):
        forms = self.parser.parse('t()(@extension E(argument))')
        t = forms[0]

        t.evaluate(self.env)

        found = self.env.lookup_extensions(t.identifier.evaluate(self.env))
        expect = [ExtensionPragma('E', [Identifier(Name('argument')).evaluate(self.env)])]

        self.assertCountEqual(found, expect)

    def test_evaluate_extension_self_name(self):
        forms = self.parser.parse('t()(@extension E(self.argument))')
        t = forms[0]

        self.env.current_self = Name(Self())
        t.evaluate(self.env)

        found = self.env.lookup_extensions(t.identifier.evaluate(self.env))
        expect = [ExtensionPragma('E', [Identifier(Self(), Name('argument'))])]

        self.assertCountEqual(found, expect)

    def test_evaluate_to_template_name(self):
        forms = self.parser.parse('t()(x=1 y=2)')
        t = forms[0]

        self.assertEqual(t.identifier.evaluate(self.env), t.evaluate(self.env))


    def test_extension_parameters(self):
        forms = self.parser.parse('t(a)(@extension AtLeastOne(a))')
        t = forms[0]

        t.evaluate(self.env)

        atleastone = self.env.lookup_extensions(t.identifier.evaluate(self.env))[0]
        arg = Identifier(t.parameters[1])

        self.assertEqual(arg, atleastone.args[0])


    def test_extension_parameters_multiple(self):
        forms = self.parser.parse('t(a, b)(@extension AtLeastOne(a, b))')
        t = forms[0]

        t.evaluate(self.env)

        atleastone = self.env.lookup_extensions(t.identifier.evaluate(self.env))[0]
        args = [Identifier(p) for p in t.parameters[1:]]

        self.assertCountEqual(args, atleastone.args)

    def test_bodied_expansion_in_template(self):
        forms = self.parser.parse('s()(a = 1)' +
                                  't()(self.e is a s()(b = 2))')
        s = forms[0]
        t = forms[1]

        s.evaluate(self.env)

        expect = [(Identifier(Self(), Name('e')),
                   Identifier(Name('a')).evaluate(self.env),
                   Value(1)),
                  (Identifier(Self(), Name('e')),
                   Identifier(Name('b')),
                   Value(2))]

        self.assertCountEqual(expect, t.as_triples(self.env))

    def test_bodied_expansion_in_template_property(self):
        forms = self.parser.parse('s()(a = 1)' +
                                  't()(x = self.e is a s()(b = 2))')
        s = forms[0]
        t = forms[1]
        s.evaluate(self.env)
        expect = [(Identifier(Self(), Name('e')),
                   Identifier(Name('a')).evaluate(self.env),
                   Value(1)),
                  (Identifier(Self(), Name('e')),
                   Identifier(Name('b')),
                   Value(2)),
                  (Identifier(Self()),
                   Identifier(Name('x')),
                   Identifier(Self(), Name('e')))]

        self.assertCountEqual(expect, t.as_triples(self.env))

    def test_as_triples_multiple_inheritance(self):
        forms = self.parser.parse('s()(a=123)' +
                                  't()(b=456)' +
                                  'u()(s() t())')

        s = forms[0]
        t = forms[1]
        u = forms[2]

        s.evaluate(self.env)
        t.evaluate(self.env)

        expect = [(Identifier(Self()),
                   Identifier(Name('a')).evaluate(self.env),
                   Value(123)),
                  (Identifier(Self()),
                   Identifier(Name('b')).evaluate(self.env),
                   Value(456))]

        self.assertEqual(expect, u.as_triples(self.env))

    def test_as_triples_nested_multiple_inheritance(self):
        forms = self.parser.parse('s()(a=123)' +
                                  't()(s() b=456)' +
                                  'u()(s() t() c=789)' +
                                  'v()(s() t() u())')

        s = forms[0]
        t = forms[1]
        u = forms[2]
        v = forms[3]

        s.evaluate(self.env)
        t.evaluate(self.env)
        u.evaluate(self.env)

        a = (Identifier(Self()), Identifier(Name('a')).evaluate(self.env), Value(123))
        b = (Identifier(Self()), Identifier(Name('b')).evaluate(self.env), Value(456))
        c = (Identifier(Self()), Identifier(Name('c')).evaluate(self.env), Value(789))

        expect = [a, a, b, a, a, b, c]

        self.assertEqual(expect, v.as_triples(self.env))

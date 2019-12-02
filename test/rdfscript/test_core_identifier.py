import unittest

from rdfscript.core import Identifier
from rdfscript.core import Name
from rdfscript.core import Uri
from rdfscript.core import Self
from rdfscript.core import Value

from rdfscript.env import Env


class TestCoreIdentifier(unittest.TestCase):

    def setUp(self):
        self.env = Env()
        self.env.current_self = Uri('')
        self.env.bind_prefix('p', Uri('prefix'))
        self.env.prefix = 'p'

    def test_identifier_equal(self):
        i1 = Identifier(Name('n1'), Name('n2'), Name('n3'))
        i2 = Identifier(Name('n1'), Name('n2'), Name('n3'))
        self.assertEqual(i1, i2)

        i3 = Identifier(Name('n1'), Name('n2'))
        self.assertNotEqual(i1, i3)

    def test_identifier_evaluate_unbound_single_name(self):
        i = Identifier(Name('first'))
        expected = Uri('prefixfirst')
        actually = i.evaluate(self.env)
        self.assertEqual(expected, actually)

    def test_identifier_evaluate_unbound_two_names(self):
        i = Identifier(Name('first'), Name('second'))
        expected = Uri('prefixfirstsecond')
        actually = i.evaluate(self.env)
        self.assertEqual(expected, actually)

    def test_identifier_evaluate_unbound_self_as_prefix(self):
        i = Identifier(Self(), Name('n'))
        expected = Identifier(Self(), Name('n'))
        actually = i.evaluate(self.env)
        self.assertEqual(expected, actually)

    def test_identifier_evaluate_multiple_unbound(self):
        i = Identifier(Name('n1'), Name('n2'), Name('n3'), Name('n4'))
        expected = Uri('prefixn1n2n3n4')
        actually = i.evaluate(self.env)
        self.assertEqual(expected, actually)

    def test_name_evaluate_bound_local(self):
        name = Name('first')
        value = Value(1)
        self.env.assign(name.evaluate(self.env), value)
        self.assertEqual(value, name.evaluate(self.env))

    def test_name_evaluate_bound_prefixed(self):

        name = Name('first', 'second')
        value = Value(1)

        self.env.assign(name.evaluate(self.env), value)
        self.assertEqual(value, name.evaluate(self.env))

    def test_name_evaluate_bound_self(self):

        name = Name(Self(), 'second')
        value = Value(1)

        self.env.assign(name.evaluate(self.env), value)
        self.assertEqual(value, name.evaluate(self.env))

    def test_name_evaluate_bound_chained(self):

        name = Name('first', 'second', 'third', 'fourth')
        value = Value(1)

        self.env.assign(name.evaluate(self.env), value)
        self.assertEqual(value, name.evaluate(self.env))

    def test_name_evaluate_chained_mix(self):

        name = Name(Self(), Uri('first'), 'third')
        value = Value(1)
        uri = Uri(self.env.current_self.uri + 'firstthird')

        self.assertEqual(name.evaluate(self.env), uri)

        self.env.assign(name.evaluate(self.env), value)
        self.assertEqual(self.env.lookup(uri), value)

    def test_name_evaluate_unbound_unresolved_self_prefix(self):

        name = Name(Self(), 'first')
        self.env.current_self = Name(Self())

        self.assertEqual(name.evaluate(self.env), Name(Self(), 'first'))

    def test_name_evaluate_unbound_unresolved_self_suffix(self):

        name = Name('first', Uri('second'), Self())
        self.env.current_self = Name(Self())

        self.assertEqual(name.evaluate(self.env), Name(
            Uri('prefixfirstsecond'), Self()))

    def test_name_evaluate_bound_prefix(self):

        name = Name('first', 'second')
        value = Uri('http://first.org/#')

        self.env.assign(Name('first').evaluate(self.env), value)

        self.assertEqual(name.evaluate(self.env),
                         Uri('http://first.org/#second'))

    def test_name_evaluate_bound_double_prefix(self):

        name = Name('first', 'second', 'third')
        value = Uri('http://first.org/#second#')

        self.env.assign(Name('first', 'second').evaluate(self.env), value)

        self.assertEqual(name.evaluate(self.env), Uri(
            'http://first.org/#second#third'))

    def test_name_evaluate_bound_prefix_not_uri(self):

        name = Name('first', 'second')
        value = Value(12345)

        self.env.assign(Name('first').evaluate(self.env), value)

        self.assertEqual(name.evaluate(self.env), Uri('prefixfirstsecond'))

    def test_name_evaluate_double_bound_prefix_not_uri(self):

        name = Name('first', 'second', 'third')
        value = Value(12345)

        self.env.assign(Name('first', 'second').evaluate(self.env), value)

        self.assertEqual(name.evaluate(self.env),
                         Uri('prefixfirstsecondthird'))

    def test_name_self_equals_self(self):

        self.assertEqual(Name(Self()), Self())
        self.assertEqual(Self(), Name(Self()))
        self.assertNotEqual(Name(Self(), 'x'), Self())

    def test_name_self_in_context(self):

        name = Name(Self(), 'name')
        context = Uri('self')

        self.env.current_self = context

        self.assertEqual(name.evaluate(self.env), Uri('selfname'))

    def test_name_self_in_unresolved_context(self):

        name = Name(Self(), 'name')
        context = Name(Self())

        self.env.current_self = context

        self.assertEqual(name.evaluate(self.env), Name(Self(), 'name'))

    def test_name_self_in_unresolved_context_self_prefix(self):

        name = Name(Self(), 'name')
        context = Name(Self(), 'name')

        self.env.current_self = context

        self.assertEqual(name.evaluate(self.env), Name(Self(), 'name', 'name'))

    def test_uri_first_unbound(self):

        name = Name(Uri('http://literal.eg/'), 'literal')

        self.assertEqual(name.evaluate(self.env),
                         Uri('http://literal.eg/literal'))

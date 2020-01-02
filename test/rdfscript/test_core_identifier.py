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

    def test_identifier_evaluate_bound_local(self):
        i = Identifier(Name('first'))
        expected = Value(1)
        self.env.assign(i.evaluate(self.env), expected)
        actually = i.evaluate(self.env)
        self.assertEqual(expected, actually)

    def test_identifier_evaluate_bound_prefixed(self):
        i = Identifier(Name('first'), Name('second'))
        expected = Value(1)
        self.env.assign(i.evaluate(self.env), expected)
        actually = i.evaluate(self.env)
        self.assertEqual(expected, actually)

    def test_identifier_evaluate_bound_multiple_parts(self):
        i = Identifier(Name('first'), Name('second'), Name('third'), Name('fourth'))
        expected = Value(1)
        self.env.assign(i.evaluate(self.env), expected)
        actually = i.evaluate(self.env)
        self.assertEqual(expected, actually)

    def test_identifier_evaluate_uri_and_symbol_parts(self):
        i = Identifier(Uri('first'), Name('second'))
        expected = Value(1)

        uri = Uri('firstsecond')
        self.assertEqual(i.evaluate(self.env), uri)

        self.env.assign(i.evaluate(self.env), expected)
        actually = i.evaluate(self.env)
        self.assertEqual(expected, actually)

    def test_identifier_evaluate_bound_prefix(self):
        i = Identifier(Name('first'), Name('second'))
        prefix = Uri('http://first.org/#')
        self.env.assign(Identifier(Name('first')).evaluate(self.env), prefix)

        expected = Uri('http://first.org/#second')
        actually = i.evaluate(self.env)
        self.assertEqual(expected, actually)

    def test_identifier_evaluate_bound_double_prefix(self):
        i = Identifier(Name('first'), Name('second'), Name('third'))
        prefix = Uri('http://first.org/#second#')
        uri = Identifier(Name('first'), Name('second')).evaluate(self.env)

        self.env.assign(uri, prefix)
        expected = Uri('http://first.org/#second#third')
        actually = i.evaluate(self.env)
        self.assertEqual(expected, actually)

    def test_identifier_evaluate_bound_prefix_not_uri(self):
        i = Identifier(Name('first'), Name('second'))
        value = Value(12345)

        self.env.assign(Identifier(Name('first')).evaluate(self.env), value)
        expected = Uri('prefixfirstsecond')
        actually = i.evaluate(self.env)
        self.assertEqual(expected, actually)

    def test_identifier_evaluate_double_bound_prefix_not_uri(self):
        i = Identifier(Name('first'), Name('second'), Name('third'))
        value = Value(12345)

        prefix_part = Identifier(Name('first'), Name('second'))
        self.env.assign(prefix_part.evaluate(self.env), value)
        expected = Uri('prefixfirstsecondthird')
        actually = i.evaluate(self.env)
        self.assertEqual(expected, actually)

    def test_identifier_uri_first_unbound(self):
        i = Identifier(Uri('http://literal.eg/'), Name('literal'))
        expected = Uri('http://literal.eg/literal')
        actually = i.evaluate(self.env)
        self.assertEqual(expected, actually)
                   

import unittest

from rdfscript.env import Env
from rdfscript.parser import Parser
from rdfscript.core import Name
from rdfscript.core import Value
from rdfscript.core import Self
from rdfscript.core import Identifier
from rdfscript.template import Property


class TestPropertyClass(unittest.TestCase):

    def setUp(self):
        self.env = Env()
        self.parser = Parser()

    def tearDown(self):
        None

    def test_as_triples_simple(self):
        p = Property(Identifier(Name('x')), Identifier(Name('y')))
        expected = [(Identifier(Self()),
                     Identifier(Name('x')),
                     Identifier(Name('y')))]
        actually = p.as_triples(self.env)
        self.assertEqual(expected, actually)

    def test_as_triples_expansion(self):
        forms = self.parser.parse('t()(x=1) e is a t()')
        t = forms[0]
        e = forms[1]
        p = Property(Identifier(Name('y')), e)

        t.evaluate(self.env)

        expected = [(Identifier(Name('e')),
                     Identifier(Name('x')).evaluate(self.env),
                     Value(1)),
                    (Identifier(Self()),
                     Identifier(Name('y')),
                     Identifier(Name('e')))]
        actually = p.as_triples(self.env)
        self.assertEqual(expected, actually)

    def test_as_triples_self_in_name(self):
        p = Property(Identifier(Self()), Value(1))
        expected = [(Identifier(Self()), Identifier(Self()), Value(1))]
        actually = p.as_triples(self.env)
        self.assertEqual(expected, actually)

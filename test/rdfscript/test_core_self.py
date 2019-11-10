import unittest

from rdfscript.core import Self, Uri, Name
from rdfscript.env import Env


class TestCoreSelf(unittest.TestCase):

    def test_self_evaluate(self):

        env = Env()
        self.assertEqual(Uri(env._rdf._g.identifier.toPython()), Self().evaluate(env))

    def test_equal_name(self):

        s = Self()

        self.assertEqual(s, s)

        n = Name(Self())

        self.assertEqual(s, n)
        self.assertEqual(n, s)
        self.assertEqual(n, n)

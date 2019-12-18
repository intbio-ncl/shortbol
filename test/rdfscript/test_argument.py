import unittest

from rdfscript.env import Env
from rdfscript.core import Value, Name, Argument, Parameter, Identifier


class TestArgumentClass(unittest.TestCase):

    def setUp(self):
        self.env = Env()

    def tearDown(self):
        None

    def test_marshal_true(self):
        p = Identifier(Parameter('z', 0))
        a = Argument(Value(1), 0)
        self.assertEqual(a.marshal(p), Value(1))

    def test_marshal_false(self):
        p = Identifier(Parameter('z', 0))
        a = Argument(Value(1), 1)
        self.assertEqual(a.marshal(p), p)

    def test_marshal_not_parameter(self):
        p = Value("string")
        a = Argument(Value(1), 0)
        self.assertEqual(a.marshal(p), p)

    def test_evaluate(self):
        a = Argument(Value(1), 0)
        self.assertEqual(a, a.evaluate(self.env))

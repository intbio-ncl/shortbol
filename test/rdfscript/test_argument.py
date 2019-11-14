import unittest

from rdfscript.env import Env
from rdfscript.core import Value, Name
from rdfscript.template import (Parameter,
                                Argument)


class TestArgumentClass(unittest.TestCase):

    def setUp(self):
        self.env = Env()

    def tearDown(self):
        None

    def test_marshal_true(self):

        p = Parameter('z', 0)
        a = Argument(Value(1), 0)

        self.assertEqual(a.marshal(p), Value(1))

    def test_marshal_false(self):

        p = Parameter('z', 0)
        a = Argument(Value(1), 1)

        self.assertEqual(a.marshal(p), p)

    def test_marshal_not_parameter(self):

        p = Value("string")
        a = Argument(Value(1), 0)

        self.assertEqual(a.marshal(p), p)

    def test_evaluate(self):

        a = Argument(Value(1), 0)

        self.assertEqual(Value(1), a.evaluate(self.env))

    def test_evaluate_name(self):

        a = Argument(Name('x'), 1)

        self.assertEqual(Name('x').evaluate(self.env), a.evaluate(self.env))

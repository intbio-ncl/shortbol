import unittest

from rdfscript.core import Name, Uri, Parameter


class TestParameterClass(unittest.TestCase):

    def setUp(self):
        None

    def tearDown(self):
        None

    def test_parameter_parameter_equality(self):
        p = Parameter('x', 0)
        q = Parameter('y', 0)
        r = Parameter('x', 0)
        self.assertNotEqual(p, q)
        self.assertEqual(p, r)

    def test_parameter_name_equality(self):
        n = Name(Parameter('x', 0))
        o = Name(Parameter('x', 0))
        self.assertEqual(n, o)

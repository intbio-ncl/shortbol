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

    def test_parameter_as_name_compare(self):

        name = Name('x')
        param = Parameter('x', 0)

        self.assertTrue(param.is_substitute(name))

        name = Name('y')
        self.assertFalse(param.is_substitute(name))

    def test_parameter_compare_to_uri(self):

        name = Name(Uri('x'))
        param = Parameter('x', 0)

        self.assertFalse(param.is_substitute(name))

    def test_parameter_compare_dotted_name(self):

        name = Name('x', 'y')
        param = Parameter('x', 0)

        self.assertFalse(param.is_substitute(name))

    def test_parameter_evaluate(self):

        param = Parameter('x', 0)
        self.assertEqual(param.evaluate(None), param)

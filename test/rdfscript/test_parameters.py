import unittest

from rdfscript.template import Parameter
from rdfscript.core import Name, Uri

class TestParameterClass(unittest.TestCase):

    def setUp(self):
        None

    def tearDown(self):
        None

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

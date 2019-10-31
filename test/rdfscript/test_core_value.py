import unittest

from rdfscript.core import Value

class TestCoreValue(unittest.TestCase):

    def test_value_string(self):

        value = Value("string")
        self.assertEqual(value.value, "string")
        self.assertEqual(value.evaluate(None), value)

    def test_value_integer(self):

        value = Value(12345)
        self.assertEqual(value.value, 12345)
        self.assertEqual(value.evaluate(None), value)

    def test_value_double(self):

        value = Value(0.12345)
        self.assertEqual(value.value, 0.12345)
        self.assertEqual(value.evaluate(None), value)

    def test_value_boolean(self):

        value = Value(True)
        self.assertEqual(value.value, True)
        self.assertEqual(value.evaluate(None), value)

        value = Value(False)
        self.assertEqual(value.value, False)
        self.assertEqual(value.evaluate(None), value)


    def test_value_equal(self):

        value1 = Value(123)
        value2 = Value(123)
        value3 = Value(124)
        value4 = Value(124.0)

        self.assertEqual(value1, value2)
        self.assertNotEqual(value1, value3)
        self.assertNotEqual(value3, value4)

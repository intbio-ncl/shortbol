import unittest

from rdfscript.core import Name, Uri, Self, Value, Assignment

from rdfscript.env import Env


class CoreAssignmentTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()

    def tearDown(self):
        None

    def test_assignment_name_string(self):

        name = Name('variable')
        value = Value("string")

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_name_integer(self):

        name = Name('variable')
        value = Value(12345)

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_name_boolean(self):

        name = Name('variable')
        value = Value(False)

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_name_double(self):

        name = Name('variable')
        value = Value(0.12345)

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_name_uri(self):

        name = Name('variable')
        value = Name(Uri('http://variable/#value'))

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_name_name(self):

        name = Name('variable')
        value = Name('value')

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_uri_string(self):

        name = Name(Uri('http://variable/#v'))
        value = Value("string")

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_uri_integer(self):

        name = Name(Uri('http://variable/#v'))
        value = Value(12345)

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_uri_boolean(self):

        name = Name(Uri('http://variable/#v'))
        value = Value(True)

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_uri_double(self):

        name = Name(Uri('http://variable/#v'))
        value = Value(1.2345)

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_uri_uri(self):

        name = Name(Uri('http://variable/#v'))
        value = Name(Uri('http://variable/#value'))

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_uri_name(self):

        name = Name(Uri('http://variable/#v'))
        value = Name('Name')

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_self_name(self):

        name = Name(Self(), 'v')
        value = Name('Name')

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

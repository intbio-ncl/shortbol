import unittest

from rdfscript.core import Name, Uri, Self, Value, Assignment, Identifier
from rdfscript.env import Env


class CoreAssignmentTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()

    def tearDown(self):
        None

    def test_assignment_name_string(self):
        name = Identifier(Name('variable'))
        value = Value("string")

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_name_integer(self):
        name = Identifier(Name('variable'))
        value = Value(12345)

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_name_boolean(self):
        name = Identifier(Name('variable'))
        value = Value(False)

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_name_double(self):
        name = Identifier(Name('variable'))
        value = Value(0.12345)

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_name_uri(self):
        name = Identifier(Name('variable'))
        value = Identifier(Uri('http://variable/#value'))

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_name_name(self):
        name = Identifier(Name('variable'))
        value = Identifier(Name('value'))

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_uri_string(self):
        name = Identifier(Uri('http://variable/#v'))
        value = Value("string")

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_uri_integer(self):
        name = Identifier(Uri('http://variable/#v'))
        value = Value(12345)

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_uri_boolean(self):
        name = Identifier(Uri('http://variable/#v'))
        value = Value(True)

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_uri_double(self):
        name = Identifier(Uri('http://variable/#v'))
        value = Value(1.2345)

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_uri_uri(self):
        name = Identifier(Uri('http://variable/#v'))
        value = Identifier(Uri('http://variable/#value'))

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    def test_assignment_uri_name(self):
        name = Identifier(Uri('http://variable/#v'))
        value = Identifier(Name('Name'))

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

    @unittest.skip("Self no longer exists outside a template/expansion")
    def test_assignment_self_name(self):
        name = Identifier(Self(), Name('v'))
        value = Identifier(Name('Name'))

        self.assertEqual(Assignment(name, value).evaluate(
            self.env), value.evaluate(self.env))
        self.assertEqual(name.evaluate(self.env), value.evaluate(self.env))

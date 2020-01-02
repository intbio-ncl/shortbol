import unittest
import logging

from rdfscript.parser import Parser
from rdfscript.core import Value
from rdfscript.core import Uri
from rdfscript.core import Self
from rdfscript.core import Name
from rdfscript.core import Assignment
from rdfscript.core import Identifier
from rdfscript.template import Expansion


class ParserAssignmentTest(unittest.TestCase):

    def setUp(self):
        self.parser = Parser()
        self.maxDiff = None
        self.logger = logging.getLogger(__name__)

    def tearDown(self):
        None

    def test_assignment_name_string(self):
        script = 'Name = "hello"'
        expected = [Assignment(Identifier(Name('Name')), Value("hello"))]
        actually = self.parser.parse(script)
        self.assertCountEqual(expected, actually)

    def test_assignment_name_integer(self):
        script = 'Name = 12345'
        expected = [Assignment(Identifier(Name('Name')), Value(12345))]
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

    def test_assignment_name_boolean(self):
        script = 'Name = true'
        expected = [Assignment(Identifier(Name('Name')), Value(True))]
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

        script = 'Name = false'
        expected = [Assignment(Identifier(Name('Name')), Value(False))]
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

    def test_assignment_name_double(self):
        script = 'Name = 0.12345'
        actually = self.parser.parse(script)
        expected = [Assignment(Identifier(Name('Name')), Value(0.12345))]
        self.assertEqual(expected, actually)

    def test_assignment_name_uri(self):
        script = 'Name = <http://uri.org/>'
        expected = [Assignment(Identifier(Name('Name')),
                               Identifier(Uri('http://uri.org/')))]
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

    def test_assignment_name_name(self):
        script = 'Name = Name'
        expected = [Assignment(Identifier(Name('Name')),
                               Identifier(Name('Name')))]
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

    def test_assignment_uri_string(self):
        script = '<http://uri.org/> = "hello"'
        expected = [Assignment(Identifier(Uri('http://uri.org/')),
                               Value("hello"))]
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

    def test_assignment_uri_integer(self):
        script = '<http://uri.org/> = 12345'
        expected = [Assignment(Identifier(Uri('http://uri.org/')),
                               Value(12345))]
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

    def test_assignment_uri_boolean(self):
        script = '<http://uri.org/> = true'
        expected = [Assignment(Identifier(Uri('http://uri.org/')),
                               Value(True))]
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

        script = '<http://uri.org/> = false'
        expected = [Assignment(Identifier(Uri('http://uri.org/')),
                               Value(False))]
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

    def test_assignment_uri_double(self):
        script = '<http://uri.org/> = 0.12345'
        expected = [Assignment(Identifier(Uri('http://uri.org/')),
                               Value(0.12345))]
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

    def test_assignment_uri_uri(self):
        script = '<http://uri.org/> = <http://value.org>'
        expected = [Assignment(Identifier(Uri('http://uri.org/')),
                               Identifier(Uri('http://value.org')))]
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

    def test_assignment_uri_name(self):
        script = '<http://uri.org/> = Name'
        expected = [Assignment(Identifier(Uri('http://uri.org/')),
                               Identifier(Name('Name')))]
        actually = self.parser.parse(script)

        self.assertEqual(expected, actually)

    def test_assignment_self_name(self):
        script = 'self.v = Name'
        expected = [Assignment(Identifier(Self(), Name('v')),
                               Identifier(Name('Name')))]
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

    def test_assignment_name_expansion(self):
        script = 'expansion = e is a t()'
        expected = [Assignment(Identifier(Name('expansion')),
                               Expansion(Identifier(Name('e')),
                                         Identifier(Name('t')),
                                         [],
                                         []))]
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

    def test_assignment_uri_expansion(self):
        script = '<expansion> = e is a t()'
        expected = [Assignment(Identifier(Uri('expansion')),
                               Expansion(Identifier(Name('e')),
                                         Identifier(Name('t')),
                                         [],
                                         []))]
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

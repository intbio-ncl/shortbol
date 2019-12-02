import unittest

from rdfscript.parser import Parser

from rdfscript.core import Name
from rdfscript.core import Uri
from rdfscript.core import Self
from rdfscript.core import Identifier


class TestIdentifierParsing(unittest.TestCase):

    def setUp(self):
        self.parser = Parser()

    def tearDown(self):
        None

    def test_identifier_single_part(self):
        script = 'n'
        expected = [Identifier(Name('n'))]
        actually = self.parser.parse(script)
        self.assertCountEqual(expected, actually)

    def test_identifier_two_parts(self):
        script = 'p.n'
        expected = [Identifier(Name('p'), Name('n'))]
        actually = self.parser.parse(script)
        self.assertCountEqual(expected, actually)

    def test_identifier_three_parts(self):
        script = 'p.n.n1'
        expected = [Identifier(Name('p'), Name('n'), Name('n1'))]
        actually = self.parser.parse(script)
        self.assertCountEqual(expected, actually)

    def test_identifier_starts_with_uri(self):
        script = '<http://prefix/>.n'
        expected = [Identifier(Uri('http://prefix/'), Name('n'))]
        actually = self.parser.parse(script)
        self.assertCountEqual(expected, actually)

    def test_identifier_ends_with_uri(self):
        script = 'p.<n>'
        expected = [Identifier(Name('p'), Uri('n'))]
        actually = self.parser.parse(script)
        self.assertCountEqual(expected, actually)

    def test_identifier_uri_in_middle(self):
        script = 'p.<n>.n1'
        expected = [Identifier(Name('p'), Uri('n'), Name('n1'))]
        actually = self.parser.parse(script)
        self.assertCountEqual(expected, actually)

    def test_identifier_uri_only(self):
        script = '<http://name.eg/#test>'
        expected = [Identifier(Uri('http://name.eg/#test'))]
        actually = self.parser.parse(script)
        self.assertCountEqual(expected, actually)

    def test_identifier_self_as_prefix(self):
        script = 'self.n'
        expected = [Identifier(Self(), Name('n'))]
        actually = self.parser.parse(script)
        self.assertCountEqual(expected, actually)

    def test_name_self_as_suffix(self):
        script = 'p.self'
        expected = [Identifier(Name('p'), Self())]
        actually = self.parser.parse(script)
        self.assertCountEqual(expected, actually)

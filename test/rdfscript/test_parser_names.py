import unittest

from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.core import Name, Uri, Self

class NameParsingTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()

    def tearDown(self):
        None

    def test_name_local(self):
        script = 'localname'
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [Name('localname')])

    def test_name_one_prefix(self):
        script = 'prefix.localname'
        forms = self.parser.parse(script)

        self.assertEqual(forms, [Name('prefix', 'localname')])

    def test_name_several_symbols(self):
        script = 'prefix.localname.morelocal'
        forms = self.parser.parse(script)

        self.assertEqual(forms, [Name('prefix', 'localname', 'morelocal')])

    def test_name_start_uri(self):
        script = '<http://prefix/>.localname'
        forms = self.parser.parse(script)

        self.assertEqual(forms, [Name(Uri('http://prefix/'), 'localname')])

    def test_name_end_uri(self):
        script = 'prefix.<localname>'
        forms = self.parser.parse(script)

        self.assertEqual(forms, [Name('prefix', Uri('localname'))])

    def test_name_middle_uri(self):
        script = 'prefix.<localname>.morelocal'
        forms = self.parser.parse(script)

        self.assertEqual(forms, [Name('prefix', Uri('localname'), 'morelocal')])

    def test_name_uri_only(self):
        script = '<http://name.eg/#test>'
        forms = self.parser.parse(script)

        self.assertEqual(forms, [Name(Uri('http://name.eg/#test'))])

    def test_name_self_prefix(self):
        script = 'self.localname'
        forms = self.parser.parse(script)

        self.assertEqual(forms, [Name(Self(), 'localname')])

    def test_name_self_suffix(self):
        script = 'prefix.self'
        forms = self.parser.parse(script)

        self.assertEqual(forms, [Name('prefix', Self())])

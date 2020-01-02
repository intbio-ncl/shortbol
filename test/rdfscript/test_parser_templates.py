import unittest
import logging

from rdfscript.parser import Parser

from rdfscript.pragma import ExtensionPragma
from rdfscript.core import Name
from rdfscript.core import Uri
from rdfscript.core import Value
from rdfscript.core import Identifier
from rdfscript.template import Template
from rdfscript.template import Expansion
from rdfscript.template import Property


class ParserTemplateTest(unittest.TestCase):

    def setUp(self):
        self.parser = Parser()
        self.maxDiff = None
        self.logger = logging.getLogger(__name__)

    def tearDown(self):
        None

    def test_template_noargs_nobase(self):
        script = 'DNASequence()(encoding = <SBOL:IUPACDNA>)'
        forms = self.parser.parse(script)
        expected_template = Template(Identifier(Name('DNASequence')),
                                     [],
                                     [Property(Identifier(Name('encoding')),
                                               Identifier(Uri('SBOL:IUPACDNA')))])
        self.assertCountEqual(forms, [expected_template])

    def test_empty_template_noargs_nobase(self):
        script = 'DNASequence()'
        forms = self.parser.parse(script)
        expected_template = Template(Identifier(Name('DNASequence')), [], [])
        self.assertCountEqual(forms, [expected_template])

    def test_empty_template_noargs(self):
        script = 'DNASequence()(Other())'
        forms = self.parser.parse(script)

        expected_template = Template(Identifier(Name('DNASequence')),
                                     [],
                                     [Expansion(None,
                                                Identifier(Name('Other')),
                                                [],
                                                [])])
        self.assertCountEqual(forms, [expected_template])

    def test_empty_template_args(self):
        script = 'DNASequence(x, y, z)(Other(x))'
        forms = self.parser.parse(script)

        expected_template = Template(Identifier(Name('DNASequence')),
                                     ['x', 'y', 'z'],
                                     [Expansion(None,
                                                Identifier(Name('Other')),
                                                [Identifier(Name('x'))],
                                                [])])
        self.assertCountEqual(forms, [expected_template])

    def test_empty_template_args_nobase(self):
        script = 'DNASequence(x, y, z)'
        forms = self.parser.parse(script)
        expected_template = Template(Identifier(Name('DNASequence')),
                                     ['x', 'y', 'z'],
                                     [])
        self.assertCountEqual(forms, [expected_template])

    def test_template_onearg_nobase(self):
        script = 'DNASequence(x)(encoding = <SBOL:IUPACDNA>)'
        forms = self.parser.parse(script)
        expected_template = Template(Identifier(Name('DNASequence')),
                                     ['x'],
                                     [Property(Identifier(Name('encoding')),
                                               Identifier(Uri('SBOL:IUPACDNA')))])
        self.assertCountEqual(forms, [expected_template])

    def test_template_multiargs_nobase(self):
        script = 'DNASequence(x, y, z)(encoding = <SBOL:IUPACDNA>)'
        forms = self.parser.parse(script)

        expected_template = Template(Identifier(Name('DNASequence')),
                                     ['x', 'y', 'z'],
                                     [Property(Identifier(Name('encoding')),
                                               Identifier(Uri('SBOL:IUPACDNA')))])
        self.assertCountEqual(forms, [expected_template])

    def test_template_onearg_base(self):
        script = 'B(x)(x = 42)\nA(x)(B(x) encoding = <SBOL:IUPACDNA>)'
        forms = self.parser.parse(script)

        expected_template = Template(Identifier(Name('A')),
                                     ['x'],
                                     [Expansion(None,
                                                Identifier(Name('B')),
                                                [Identifier(Name('x'))],
                                                []),
                                      Property(Identifier(Name('encoding')),
                                               Identifier(Uri('SBOL:IUPACDNA')))])
        self.assertCountEqual([forms[1]], [expected_template])

    def test_expansion_in_property(self):
        script = 'A()(x = e is a B())'
        forms = self.parser.parse(script)
        e = self.parser.parse('e is a B()')[0]

        expected_template = Template(Identifier(Name('A')),
                                     [],
                                     [Property(Identifier(Name('x')), e)])
        self.assertEqual(expected_template, forms[0])

    def test_expansion_in_property_with_body(self):
        script = 'A()(x = e is a B()(y = 12345))'
        forms = self.parser.parse(script)
        e = self.parser.parse('e is a B()(y = 12345)')[0]
        expected_template = Template(Identifier(Name('A')),
                                     [],
                                     [Property(Identifier(Name('x')), e)])
        self.assertEqual(expected_template, forms[0])

    def test_expansion_in_body_with_body(self):
        script = 'A()(e is a B()(y = 12345))'
        forms = self.parser.parse(script)
        e = self.parser.parse('e is a B()(y = 12345)')[0]
        expected_template = Template(Identifier(Name('A')),
                                     [],
                                     [e])
        self.assertEqual(expected_template, forms[0])

    def test_expansion_in_body(self):
        script = 'A()(e is a B())'
        forms = self.parser.parse(script)
        e = self.parser.parse('e is a B()')[0]
        expected_template = Template(Identifier(Name('A')),
                                     [],
                                     [e])
        self.assertEqual(expected_template, forms[0])

    def test_expansion_in_property_with_args(self):
        script = 'A()(x = e is a B(12345))'
        forms = self.parser.parse(script)
        e = self.parser.parse('e is a B(12345)')[0]
        expected_template = Template(Identifier(Name('A')),
                                     [],
                                     [Property(Identifier(Name('x')), e)])
        self.assertEqual(expected_template, forms[0])

    def test_expansion_in_body_with_args(self):
        script = 'A()(e is a B(12345))'
        forms = self.parser.parse(script)
        e = self.parser.parse('e is a B(12345)')[0]
        expected_template = Template(Identifier(Name('A')),
                                     [],
                                     [e])
        self.assertEqual(expected_template, forms[0])

    def test_extension_in_body(self):
        script = 'A()(@extension ExtensionName())'
        forms = self.parser.parse(script)
        a = forms[0]
        expected_template = Template(Identifier(Name('A')),
                                     [],
                                     [ExtensionPragma('ExtensionName', [])])
        self.assertEqual(expected_template, a)

    def test_extension_in_body_with_arg(self):
        script = 'A()(@extension ExtensionName(12345))'
        forms = self.parser.parse(script)
        a = forms[0]
        expected_template = Template(Identifier(Name('A')),
                                     [],
                                     [ExtensionPragma('ExtensionName', [Value(12345)])])
        self.assertEqual(expected_template, a)

    def test_extension_in_body_with_multi_args(self):
        script = 'A()(@extension ExtensionName(12345, 67890))'
        forms = self.parser.parse(script)
        a = forms[0]
        expected_template = Template(Identifier(Name('A')),
                                     [],
                                     [ExtensionPragma('ExtensionName',
                                                      [Value(12345),
                                                       Value(67890)])])
        self.assertEqual(expected_template, a)


if __name__ == '__main__':
    unittest.main()

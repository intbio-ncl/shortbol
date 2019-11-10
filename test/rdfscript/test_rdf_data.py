import unittest

import rdflib

from rdfscript.core import Uri, Value
from rdfscript.rdf_data import RDFData

class RDFDataTest(unittest.TestCase):

    def setUp(self):
        None

    def tearDown(self):
        None

    def test_init(self):

        data = RDFData()
        self.assertEqual(data._serializer, None)

        data = RDFData(serializer='turtle')
        self.assertEqual(data._serializer, 'turtle')

    def test_namespace(self):

        data = RDFData()
        self.assertEqual(data.namespace, Uri(data._g.identifier.toPython(), None))

    def test_to_rdf(self):

        data = RDFData()
        self.assertEqual(rdflib.URIRef('http://test.org/#'), data.to_rdf(Uri('http://test.org/#', None)))
        self.assertEqual(rdflib.URIRef(''), data.to_rdf(Uri('', None)))
        self.assertEqual(rdflib.Literal(42), data.to_rdf(Value(42, None)))
        self.assertEqual(rdflib.Literal("String"), data.to_rdf(Value("String", None)))
        self.assertEqual(rdflib.Literal(True), data.to_rdf(Value(True, None)))
        self.assertEqual(rdflib.Literal(0.12345), data.to_rdf(Value(0.12345, None)))

    def test_from_rdf(self):

        data = RDFData()
        self.assertEqual(Uri('http://namespace.eg/', None), data.from_rdf(rdflib.Namespace('http://namespace.eg/')))
        self.assertEqual(Uri('http://uri.org/', None), data.from_rdf(rdflib.URIRef('http://uri.org/')))
        self.assertEqual(Value(42, None), data.from_rdf(rdflib.Literal(42)))
        self.assertEqual(Value(False, None), data.from_rdf(rdflib.Literal(False)))
        self.assertEqual(Value("String", None), data.from_rdf(rdflib.Literal("String")))

    def test_add(self):

        data = RDFData()
        (s, p, o) = (Uri('http://subject.com/', None), Uri('http://predicate.com/', None), Value(123, None))

        data.add(s, p, o)

        rdf_triple = (rdflib.URIRef('http://subject.com/'),
                      rdflib.URIRef('http://predicate.com/'),
                      rdflib.Literal(123))

        self.assertEqual(next(data._g.triples((None, None, None))), rdf_triple)

    def test_bind_get_prefix(self):

        data = RDFData()

        prefixes = [p for (p, n) in data._g.namespaces()]
        self.assertFalse('test_prefix' in prefixes)

        data.bind_prefix('test_prefix', Uri('http://prefix.org/#', None))

        prefixes = list(data._g.namespaces())
        self.assertTrue(('test_prefix', rdflib.URIRef('http://prefix.org/#')) in prefixes)

    def test_uri_for_prefix(self):

        data = RDFData()

        data.bind_prefix('test_prefix', Uri('http://prefix.org/#', None))

        self.assertEqual(data.uri_for_prefix('test_prefix'), Uri('http://prefix.org/#', None))

    def test_prefix_for_uri(self):

        data = RDFData()

        data.bind_prefix('test_prefix', Uri('http://prefix.org/#', None))

        self.assertEqual(data.prefix_for_uri(Uri('http://prefix.org/#', None)), 'test_prefix')




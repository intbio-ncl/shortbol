import unittest

import rdflib
from rdfscript.core import Name, Uri, Self, Value

class CoreUriTest(unittest.TestCase):

    def setUp(self):
        None

    def tearDown(self):
        None

    def test_init_with_rdflib(self):

        uri = Uri(rdflib.URIRef('exampleuri'))
        self.assertEqual(uri.uri, 'exampleuri')

    def test_init_with_uri(self):

        uri = Uri(Uri('exampleuri'))
        self.assertEqual(uri.uri, 'exampleuri')

    def test_init_with_string(self):

        uri = Uri('exampleuri')
        self.assertEqual(uri.uri, 'exampleuri')

    def test_evaluate(self):

        uri = Uri('exampleuri')

        self.assertEqual(uri.evaluate(None), uri)

    def test_equal(self):

        uri1 = Uri(rdflib.URIRef('exampleuri'))
        uri2 = Uri('exampleuri')
        uri3 = Uri(uri2)

        self.assertEqual(uri1, uri2, uri3)

        uri4 = Uri('anotherexample')
        self.assertNotEqual(uri4, uri1)
        self.assertNotEqual(uri4, uri2)
        self.assertNotEqual(uri4, uri3)

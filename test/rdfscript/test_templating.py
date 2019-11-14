import unittest

loader = unittest.TestLoader()

suite = unittest.TestSuite()
suite.addTests(loader.loadTestsFromNames(['test.rdfscript.test_template',
                                          'test.rdfscript.test_expansion',
                                          'test.rdfscript.test_argument',
                                          'test.rdfscript.test_parameters',
                                          'test.rdfscript.test_property']))

runner = unittest.TextTestRunner()
result = runner.run(suite)

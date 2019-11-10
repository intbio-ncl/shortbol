import unittest

loader = unittest.TestLoader()
suite = loader.discover('./test/rdfscript/', pattern='test_*.py')
runner = unittest.TextTestRunner()
result = runner.run(suite)

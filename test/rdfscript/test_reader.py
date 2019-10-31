import unittest

loader = unittest.TestLoader()
suite = loader.discover('.', pattern='test_reader_*.py')
runner = unittest.TextTestRunner()
result = runner.run(suite)

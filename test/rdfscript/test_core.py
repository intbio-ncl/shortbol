import unittest

loader = unittest.TestLoader()
suite = loader.discover('.', pattern='test_core_*.py')
runner = unittest.TextTestRunner()
result = runner.run(suite)

import unittest

import os, sys
sys.path.insert(1, os.path.join(sys.path[0], '..',".."))
import run

test_files =os.path.join("tutorial_examples")
templates = os.path.join("..","..","templates")
output_fn = "test_output.xml"
class TestRegression(unittest.TestCase):
    '''
    Test full system by checking final output so that we can check if any bugs have been added by chages
    '''

    def setUp(self):
        None

    def tearDown(self):
        try:
            os.remove(os.path.join(test_files,"temporary_runner.rdfsh"))
            os.remove(output_fn)
        except FileNotFoundError:
            None

    def test_regression_by_examples(self):
        failure_exceptions = []
        for path, subdirs, files in os.walk(test_files):
            print("js")
            for name in files:
                if name.endswith(".rdfsh") or name.endswith(".txt"):
                    file_to_run = os.path.join(path, name)
                    
                    print("Running with file: " + str(file_to_run))
                    return_code = "Error Thrown."
                    try:
                        return_code = run.parse_from_file(file_to_run,"sbolxml",[templates],output_fn,[])
                    except Exception as e:
                        failure_exceptions.append({file_to_run:e})
                    self.assertEqual(return_code,"Valid.","When Testing with file: " + file_to_run)
        for k,v in failure_exceptions:
            print("Failure by Exception on:" + k + ", Exception: " + str(v))
        if len(failure_exceptions) > 0:
            self.fail("A test script failed by exception.")

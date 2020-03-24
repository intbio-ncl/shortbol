import unittest

import os, sys
sys.path.insert(1, os.path.join(sys.path[0], '..',".."))
import run

test_files =os.path.join("..","..","examples")
templates = os.path.join("..","..","templates")
output_fn = "output_shortbol.xml"
class TestRegression(unittest.TestCase):
    '''
    Test full system by checking final output so that we can check if any bugs have been added by chages
    '''

    def setUp(self):
        None

    def tearDown(self):
        try:
            os.remove(os.path.join(test_files,"temporary_runner.shb"))
            os.remove(output_fn)
        except FileNotFoundError:
            None

    def test_regression_by_examples(self):
        failure_exceptions = []
        sbol_validation_errors=[]
        for path, subdirs, files in os.walk(test_files):
            for name in files:
                if name == "temporary_runner.shb":
                    continue
                if name.endswith(".shb") or name.endswith(".txt"):
                    if "sbol_3" in path:
                        version = "sbol_3"
                    else:
                        version = "sbol_2"
                    file_to_run = os.path.join(path, name)
                    short_fn = file_to_run.split("\\")
                    short_fn = "/".join(short_fn[len(short_fn) - 2 : ])
                    print("Running with file: " + str(short_fn))
                    return_code = "Error Thrown."
                    try:
                        return_code = run.parse_from_file(file_to_run,"sbolxml",[templates],output_fn,[],version=version)
                    except Exception as e:
                        failure_exceptions.append({file_to_run : e})
                    if return_code != {"SBOL validator success.":[]}:
                        sbol_validation_errors.append({short_fn : return_code})
        
        print("--------------------Report--------------------\n")
        print(f"Number of failures by exception: {str(len(failure_exceptions))}")
        print(f"Number of failures by validation: {str(len(sbol_validation_errors))}")

        if len(failure_exceptions) > 0:
            for exception in failure_exceptions:
                for k,v in exception.items():
                    print("Failure by Exception on:" + k + ", Exception: " + str(v))
            

        if len(sbol_validation_errors) > 0:
            for validation_error in sbol_validation_errors:
                for k,v in validation_error.items():
                    print("Failure by SBOL Validation on: " + str(k) + "\nvalidation errors: " + str(v) + "\n")

        if len(failure_exceptions) > 0 or len(sbol_validation_errors) > 0:
            self.fail("Atleast One Test Failed")
        
        print("\n--------------------------------------------")
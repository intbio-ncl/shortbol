import unittest

import os, sys
sys.path.insert(1, os.path.join(sys.path[0], '..',".."))
import run
import rdf_diff_checker
from sbol_tests import *
shortbol_test_files = os.path.join("shortbol_examples")
sbol_test_files = os.path.join("sbol_tests")
templates = os.path.join("..","..","templates")
sbol_output_fn = "sbol_output.xml"
shortbol_output_fn = "shortbol_output.xml"
class TestDifference(unittest.TestCase):
    '''
    Attempt to create the same theorical output from pySBOL and ShortBOL to find any difference.
    Inspect to check if any possible bugs on ShortBOL's end may be present.
    '''

    def setUp(self):
        None

    def tearDown(self):
        try:
            os.remove(os.path.join(sbol_test_files,"temporary_runner.rdfsh"))
            os.remove(output_fn)
        except FileNotFoundError:
            None

    def test_regression_by_examples(self):
        failure_exceptions = []
        for path, subdirs, files in os.walk(shortbol_test_files):
            for name in files:
                if name.endswith(".shb") or name.endswith(".txt"):
                    shortbol_file_to_run = os.path.join(path, name)
                    sbol_file_to_run = os.path.join(sbol_test_files,name.split(".")[0]+".py")
                    if not os.path.isfile(sbol_file_to_run):
                        continue

                    print(f' Comparing {shortbol_file_to_run} with {sbol_file_to_run}')
                    return_code = "Error Thrown."
                    return_code_shortbol = run.parse_from_file(shortbol_file_to_run,"sbolxml",[templates],shortbol_output_fn,[])


                    #print("Running: " + str(sbol_file_to_run))
                    os.system("python " + sbol_file_to_run)

                    exit(0)



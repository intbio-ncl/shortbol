import unittest

import os, sys
sys.path.insert(1, os.path.join(sys.path[0], '..',".."))
import run
import rdf_diff_checker
from sbol_tests import *

shortbol_test_files = os.path.join("shortbol_tests")
sbol_test_files = os.path.join("sbol_tests")
templates = os.path.join("..","..","templates")
sbol_output_fn = "pysbol_output.xml"
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

    def test_difference_single_component_definition(self):
        shortbol_input = os.path.join(shortbol_test_files,"test_difference_single_component_definition.shb")
        pysbol_input = os.path.join(sbol_test_files,"test_difference_single_component_definition.py")

        run_pysbol(pysbol_input)
        run_shortbol(shortbol_input)

        if not os.path.isfile(sbol_output_fn) or not os.path.isfile(shortbol_output_fn):
            self.fail(f'Comparrison files no not exsit.')


        rdf_diff_checker.rdf_difference_check(shortbol_output_fn,sbol_output_fn)

def run_shortbol(filename):
    return_code_shortbol = run.parse_from_file(filename,"sbolxml",[templates],shortbol_output_fn,[])
    return return_code_shortbol

def run_pysbol(filename):
    os.system("python " + filename)

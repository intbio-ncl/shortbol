import os
import sys
sys.path.insert(0,os.path.expanduser(os.path.join("..","..","..")))

import unittest
import shutil
import rdflib
import SBOL2ShortBOL
import run as shortbol_script_runner

test_files = os.path.join(".")
templates = os.path.join("..","..","..","templates")

class TestRegression(unittest.TestCase):
    '''
    Test full system by checking final output so that we can check if any bugs have been added by chages
    '''

    def setUp(self):
        None

    def tearDown(self):
        try:
            pass
        except FileNotFoundError:
            None

    

    def test_non_sbol_produced(self):
        # For each example in the examples_dir
        diff_errors = []
        sbol_validation_errors = {}

        for path, subdirs, files in os.walk(test_files):
            if "extensions" in path:
                continue
            for name in files:
                if name == "temporary_runner.shb":
                    continue
                if name.endswith(".xml"):
                    
                    file_to_run = os.path.join(path, name)
                    log_dir = os.path.join(os.getcwd(),name.split(".")[0])
                    try:
                        os.mkdir(log_dir)
                    except FileExistsError:
                        pass
                    print("\n----------------------------------------")
                    print(f'Running Regression test with {file_to_run}')
                    shortbol_code = os.path.join(log_dir,"shortbol_code.shb")
                    second_rdf_fn = os.path.join(log_dir,"final_output.rdf")

                    try:
                        SBOL2ShortBOL.produce_shortbol(file_to_run, templates, shortbol_code, True)
                    except ValueError:
                        self.fail("Unable to produce the ShortBOL code.")
                    # ShortBOL 2 SBOL - Produce RDF from new ShortBOL.
                    ret_code = produce_sbol(shortbol_code,second_rdf_fn)
                    if not ret_code == {'SBOL validator success.': []}:
                        print("Test failed due to generated ShortBOL producing Invalid SBOL.")
                        sbol_validation_errors[file_to_run] = ret_code

                    # Load the original RDF and Newer RDF into a graph and compare.
                    log_fn = os.path.join(log_dir,"error_log.txt")
                    if rdf_difference_check(file_to_run,second_rdf_fn,log_fn):
                        print("Test Passed")
                        shutil.rmtree(log_dir)
                    else:
                        print("Test failed due to differences in SHB files.")
                        diff_errors.append(file_to_run)
                    print("----------------------------------------")

        if len(list(sbol_validation_errors.keys())) > 0:
            print("ERROR:: Produced invalid ShortBOL.")
            for k,v in sbol_validation_errors.items():
                print(k,v)
        if len(diff_errors) != 0:
            print(f"Regressed with {len(diff_errors)} number of tests")
            print("ERROR:: Differences found during testing")
            for e in diff_errors:
                print(e)
            self.fail("Failed due to differences")
        



def produce_sbol(fn,output):
    try:
        return_code = shortbol_script_runner.parse_from_file(fn,"sbolxml",[templates],output,[])
    except Exception as e:
        return e
    return return_code

def rdf_difference_check(file1,file2,log_fn):
    if not os.path.isfile(file1) or not os.path.isfile(file2):
        return False
    g1 = rdflib.Graph()
    g1.load(file1)
    iso1 = rdflib.compare.to_isomorphic(g1)
    g2 = rdflib.Graph()
    g2.load(file2)

    iso2 = rdflib.compare.to_isomorphic(g2)
    rdf_diff = rdflib.compare.graph_diff(iso1, iso2)

    if rdf_diff[1] or rdf_diff[2]:
        f = open(log_fn,"a")
        f.write(f'{len(rdf_diff[1]) + len(rdf_diff[2])} differences found.\n')
        f.write(f'Differences:\n')
        for stmt in rdf_diff[1]:
            f.write(str(stmt))
            f.write("\n")
        for stmt in rdf_diff[2]:
            f.write(f'Only in loaded: {str(stmt)}\n')
        f.close()
        return False
    else:
        return True

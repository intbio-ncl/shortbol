
import unittest
import os
import sys
import rdflib
sys.path.insert(0,os.path.expanduser(os.path.join("..","..","..","..")))
import SBOL2ShortBOL
import run as shortbol_script_runner

lib_path = os.path.join("..","..","..","..","templates")
output_fn = "test_out.rdf"

sbolns = rdflib.URIRef('http://sbols.org/v2#')
default_shortbol_namespace = rdflib.URIRef('http://sbol_prefix.org')
rdf_syntax_type = rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
version_1 = rdflib.Literal('1')


class FindRootsTest(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_component_definition(self):
        '''
        Simplest Test only one triplepack in the form of a ComponentDefinition TopLevel.
        '''
        # Create SBOL from ShortBOL
        test_fn = "test_component_definition.shb"
        return_code = shortbol_script_runner.parse_from_file(test_fn,optpaths=[lib_path],out=output_fn)
        self.assertEqual(list(return_code.keys())[0], "SBOL validator success.")
        test_graph = rdflib.Graph()
        test_graph.load(output_fn)

        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),1)
        expected_roots = {( default_shortbol_namespace + "/n/" + version_1, 
                           rdf_syntax_type, 
                           sbolns + "ComponentDefinition")}

        self.assertCountEqual(roots,expected_roots)


    def test_all_top_level(self):
        '''
        Tests all implemented TopLevel Templates only.
        '''
        test_fn = "test_all_top_level.shb"
        # Create SBOL from ShortBOL
        return_code = shortbol_script_runner.parse_from_file(test_fn,optpaths=[lib_path],out=output_fn)
        self.assertEqual(list(return_code.keys())[0], "SBOL validator success.")
        test_graph = rdflib.Graph()
        test_graph.load(output_fn)

        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)

        self.assertEqual(len(roots),3)
        expected_roots = {( default_shortbol_namespace + "/q/" + version_1, 
                           rdf_syntax_type, 
                           sbolns + "ComponentDefinition"),

                           (default_shortbol_namespace + "/a/" + version_1, 
                           rdf_syntax_type, 
                           sbolns + "ModuleDefinition"),

                           (default_shortbol_namespace + "/z/" + version_1, 
                           rdf_syntax_type, 
                           sbolns + "Model")}


    def test_no_top_level(self):
        '''
        Tests a file that contains NO top level (Root) templates.
        '''
        test_fn = "test_no_top_level.shb"
        # Create SBOL from ShortBOL
        return_code = shortbol_script_runner.parse_from_file(test_fn,optpaths=[lib_path],out=output_fn)
        test_graph = rdflib.Graph()
        test_graph.load(output_fn)

        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)

        self.assertEqual(len(roots),0)


    def test_mixed_1(self):
        '''
        Random Test Files that contain mixed top-level and non-toplevel 
        objects with parent-child relationships.
        (Note this example shows a weird problem with SBOL where components)
        '''
        test_fn = "test_mixed_1.shb"
        # Create SBOL from ShortBOL
        return_code = shortbol_script_runner.parse_from_file(test_fn,optpaths=[lib_path],out=output_fn)
        self.assertEqual(list(return_code.keys())[0], "SBOL validator success.")
        test_graph = rdflib.Graph()
        test_graph.load(output_fn)

        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),9)
        expected_roots = {}


    def test_mixed_2(self):
        '''
        Random Test Files that contain mixed top-level and non-toplevel 
        objects with parent-child relationships.
        (Note this example shows a weird problem with SBOL where components)
        '''
        test_fn = "test_mixed_2.shb"
        # Create SBOL from ShortBOL
        return_code = shortbol_script_runner.parse_from_file(test_fn,optpaths=[lib_path],out=output_fn)
        self.assertEqual(list(return_code.keys())[0], "SBOL validator success.")
        test_graph = rdflib.Graph()
        test_graph.load(output_fn)

        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),3)
        expected_roots = {}



    def test_mixed_3(self):
        '''
        Random Test Files that contain mixed top-level and non-toplevel 
        objects with parent-child relationships.
        (Note this example shows a weird problem with SBOL where components)
        '''
        test_fn = "test_mixed_3.shb"
        # Create SBOL from ShortBOL
        return_code = shortbol_script_runner.parse_from_file(test_fn,optpaths=[lib_path],out=output_fn)
        self.assertEqual(list(return_code.keys())[0], "SBOL validator success.")
        test_graph = rdflib.Graph()
        test_graph.load(output_fn)

        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),4)
        expected_roots = {}






    def test_invalid_sbol_top_level_with_parent(self):
        '''
        Test to check the get_roots can find invalid graphs where top_level objects
        Have parents.
        '''

        test_fn = "test_invalid_sbol_top_level_with_parent_smaller.rdf"
        test_graph = rdflib.Graph()
        test_graph.load(test_fn)

        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)  
        self.assertEqual(len(roots),3)
        expected_roots = {}





import unittest
import os
import sys
import rdflib
sys.path.insert(0,os.path.expanduser(os.path.join("..","..","..","..")))
import SBOL2ShortBOL
import run as shortbol_script_runner

lib_path = os.path.join("..","..","..","..","templates")
output_fn = "test_out.rdf"
rdf_syntax_type = rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
output_dir = "output"

class FindRootsTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        if os.path.isfile("test_out.rdf"):
            os.remove("test_out.rdf")


    def common_tests(self,heirachy_tree,roots):
        # General tests that we know must be true on every tree
        self.assertCountEqual(list(heirachy_tree.keys()), [str(root[0]) for root in roots])
        def test_inner(item):
            for parent,triples in item.items():
                self.assertEqual(type(parent[1]),str)
                properties = set([triple[1] for triple in triples if not isinstance(triple,dict)])
                self.assertTrue(rdf_syntax_type in properties)
                # Check if all required properties have been captured.
                if not SBOL2ShortBOL.required_properties.issubset(properties):
                    print(f'{parent} does not have: {SBOL2ShortBOL.required_properties.difference(properties)}')
                for properties in triples:
                    if isinstance(properties,tuple):
                        # The property of triple is the parent.
                        self.assertEqual(str(properties[0]),parent)
                        # The parent is never the subject or object of triple
                        self.assertNotEqual(str(properties[1]),parent)
                        self.assertNotEqual(str(properties[1]),parent)
                    elif isinstance(properties,dict):
                        test_inner(properties)
        test_inner(heirachy_tree)


    def test_level_0(self):
        '''
        Simplest Test only one triplepack with no children.
        Expect: Single tree, cd as root with only a single layer that only contains the properties
                of the CD no children references.
        '''
        # Create SBOL from ShortBOL
        test_fn = "test_level_0.shb"
        return_code = shortbol_script_runner.parse_from_file(test_fn,optpaths=[lib_path],out=output_fn)
        self.assertEqual(list(return_code.keys())[0], "SBOL validator success.")
        test_graph = load_graph(output_fn)
        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),1)
        # Test get_tree
        heirachy_tree = generate_tree(roots,test_graph)
        SBOL2ShortBOL.tree_dump(heirachy_tree, os.path.join(output_dir,test_fn.split(".")[0] + ".txt"))

        self.common_tests(heirachy_tree,roots)

        # Bespoke tests that can only be done by knowledge of the graph.
        single_cd = heirachy_tree[str(list(roots)[0][0])]
        expected_type = (rdflib.URIRef('http://sbol_prefix.org/n/1') , rdflib.URIRef('http://sbols.org/v2#type'), rdflib.URIRef('http://www.biopax.org/release/biopax-level3.owl#Dna'))
        expected_name = (rdflib.URIRef('http://sbol_prefix.org/n/1') , rdflib.URIRef('http://purl.org/dc/terms/title'), rdflib.term.Literal('LacI CDS'))
        expected_description = (rdflib.URIRef('http://sbol_prefix.org/n/1') , rdflib.URIRef('http://purl.org/dc/terms/description'), rdflib.term.Literal('Coding Region for LacI protein'))
        expected_role = (rdflib.URIRef('http://sbol_prefix.org/n/1') , rdflib.URIRef('http://sbols.org/v2#role'), rdflib.URIRef('http://identifiers.org/so/SO:0000316'))
        self.assertEqual(len(heirachy_tree),1)
        self.assertTrue(expected_type in single_cd)
        self.assertTrue(expected_name in single_cd)
        self.assertTrue(expected_description in single_cd)
        self.assertTrue(expected_role in single_cd)

        top_level_count,children = count_objects(heirachy_tree)
        child_count = sum(list(children.values()))
        self.assertEqual(top_level_count,1)
        self.assertEqual(child_count,0)
        self.assertEqual(children["http://sbol_prefix.org/n/1"],0)

        max_depth,depths = get_depth(heirachy_tree)
        self.assertEqual(max_depth,0)
        self.assertEqual(depths["http://sbol_prefix.org/n/1"],0)


    def test_level_1(self):
        '''
        Test that runs with a single parent-child relationship
        Expect: Two trees (Two Component Definitions) but with a relationship triplepack
                This is a component that is a child of one of the CDS
        '''
        # Create SBOL from ShortBOL
        test_fn = "test_level_1.shb"
        return_code = shortbol_script_runner.parse_from_file(test_fn,optpaths=[lib_path],out=output_fn)
        self.assertEqual(list(return_code.keys())[0], "SBOL validator success.")
        test_graph = load_graph(output_fn)
        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),2)
        # Test get_tree
        heirachy_tree = generate_tree(roots,test_graph)
        SBOL2ShortBOL.tree_dump(heirachy_tree, os.path.join(output_dir,test_fn.split(".")[0] + ".txt"))

        self.common_tests(heirachy_tree,roots)

        # Bespoke tests that can only be done by knowledge of the graph.
        # The tree has two roots
        top_level_count,children = count_objects(heirachy_tree)
        child_count = sum(list(children.values()))
        self.assertEqual(top_level_count,2)
        self.assertEqual(child_count,1)
        self.assertEqual(children["http://sbol_prefix.org/pTetR/1"],0)
        self.assertEqual(children["http://sbol_prefix.org/tetRInverter/1"],1)

        max_depth,depths = get_depth(heirachy_tree)
        self.assertEqual(max_depth,1)
        self.assertEqual(depths["http://sbol_prefix.org/pTetR/1"],0)
        self.assertEqual(depths["http://sbol_prefix.org/tetRInverter/1"],1)
        
    
    def test_level_2(self):
        '''
        Test that runs with GrandParent - Child Relationship
        Expect: Two trees (Two Component Definitions) with two relationships
                This is a component that is a child of one of the CDS with a SequenceAnnotation and a child Location.
        '''
        # Create SBOL from ShortBOL
        test_fn = "test_level_2.shb"
        return_code = shortbol_script_runner.parse_from_file(test_fn,optpaths=[lib_path],out=output_fn)
        self.assertEqual(list(return_code.keys())[0], "SBOL validator success.")
        test_graph = load_graph(output_fn)
        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),2)
        # Test get_tree
        heirachy_tree = generate_tree(roots,test_graph)
        SBOL2ShortBOL.tree_dump(heirachy_tree, os.path.join(output_dir,test_fn.split(".")[0] + ".txt"))

        self.common_tests(heirachy_tree,roots)

        # Bespoke tests that can only be done by knowledge of the graph.
        # The tree has two roots
        top_level_count,children = count_objects(heirachy_tree)
        child_count = sum(list(children.values()))
        self.assertEqual(top_level_count,2)
        self.assertEqual(child_count,3)
        self.assertEqual(children["http://sbol_prefix.org/pTetR/1"],0)
        self.assertEqual(children["http://sbol_prefix.org/tetRInverter/1"],3)

        max_depth,depths = get_depth(heirachy_tree)
        self.assertEqual(max_depth,2)
        self.assertEqual(depths["http://sbol_prefix.org/pTetR/1"],0)
        self.assertEqual(depths["http://sbol_prefix.org/tetRInverter/1"],2)

    def test_level_2_2(self):
        '''
        Test that runs with GrandParent - Child Relationship
        Expect: Two trees (Two Component Definitions) with two relationships
                This is a component that is a child of one of the CDS with a SequenceAnnotation and a child Location.
        '''
        # Create SBOL from ShortBOL
        test_fn = "test_level_2_2.shb"
        return_code = shortbol_script_runner.parse_from_file(test_fn,optpaths=[lib_path],out=output_fn)
        self.assertEqual(list(return_code.keys())[0], "SBOL validator success.")
        test_graph = load_graph(output_fn)
        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),3)
        # Test get_tree
        heirachy_tree = generate_tree(roots,test_graph)
        SBOL2ShortBOL.tree_dump(heirachy_tree, os.path.join(output_dir,test_fn.split(".")[0] + ".txt"))

        self.common_tests(heirachy_tree,roots)

        # Bespoke tests that can only be done by knowledge of the graph.
        # The tree has two roots
        top_level_count,children = count_objects(heirachy_tree)
        child_count = sum(list(children.values()))
        self.assertEqual(top_level_count,3)
        self.assertEqual(child_count,5)
        self.assertEqual(children["http://sbol_prefix.org/cd1/1"],0)
        self.assertEqual(children["http://sbol_prefix.org/cd2/1"],0)
        self.assertEqual(children["http://sbol_prefix.org/moduledef_1/1"],5)

        max_depth,depths = get_depth(heirachy_tree)
        self.assertEqual(max_depth,2)
        self.assertEqual(depths["http://sbol_prefix.org/cd1/1"],0)
        self.assertEqual(depths["http://sbol_prefix.org/cd2/1"],0)
        self.assertEqual(depths["http://sbol_prefix.org/moduledef_1/1"],2)
        

    def test_many_trees(self):
        '''
        Test that runs many top-level objects BUT with no children.
        Expect: Each Top-Level Object in the template libary is its own tree.
        '''
        # Create SBOL from ShortBOL
        test_fn = "test_many_trees.shb"
        return_code = shortbol_script_runner.parse_from_file(test_fn,optpaths=[lib_path],out=output_fn)
        self.assertEqual(list(return_code.keys())[0], "SBOL validator success.")
        test_graph = load_graph(output_fn)
        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),4)
        # Test get_tree
        heirachy_tree = generate_tree(roots,test_graph)
        SBOL2ShortBOL.tree_dump(heirachy_tree, os.path.join(output_dir,test_fn.split(".")[0] + ".txt"))

        self.common_tests(heirachy_tree,roots)

        # Bespoke tests that can only be done by knowledge of the graph.
        # The tree has two roots
        top_level_count,children = count_objects(heirachy_tree)
        child_count = sum(list(children.values()))
        self.assertEqual(top_level_count,4)
        self.assertEqual(child_count,0)
        self.assertEqual(children["http://sbol_prefix.org/seq_1/1"],0)
        self.assertEqual(children["http://sbol_prefix.org/cd_1/1"],0)
        self.assertEqual(children["http://sbol_prefix.org/mod_def_1/1"],0)
        self.assertEqual(children["http://sbol_prefix.org/module_1/1"],0)

        max_depth,depths = get_depth(heirachy_tree)
        self.assertEqual(max_depth,0)
        self.assertEqual(depths["http://sbol_prefix.org/seq_1/1"],0)
        self.assertEqual(depths["http://sbol_prefix.org/cd_1/1"],0)
        self.assertEqual(depths["http://sbol_prefix.org/mod_def_1/1"],0)
        self.assertEqual(depths["http://sbol_prefix.org/module_1/1"],0)

    def test_many_trees_many_relationships(self):
        '''
        Test that runs many top-level objects AND with many relationships but all depth-2 level relationships.
        Expect: Each Top-Level objects are connected by non-top-level object, parent-child relationships.
        '''
        # Create SBOL from ShortBOL
        test_fn = "test_many_trees_many_relationships.shb"
        return_code = shortbol_script_runner.parse_from_file(test_fn,optpaths=[lib_path],out=output_fn)
        self.assertEqual(list(return_code.keys())[0], "SBOL validator success.")
        test_graph = load_graph(output_fn)
        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),5)
        # Test get_tree
        heirachy_tree = generate_tree(roots,test_graph)
        SBOL2ShortBOL.tree_dump(heirachy_tree, os.path.join(output_dir,test_fn.split(".")[0] + ".txt"))

        self.common_tests(heirachy_tree,roots)

        # Bespoke tests that can only be done by knowledge of the graph.
        # The tree has two roots
        top_level_count,children = count_objects(heirachy_tree)
        child_count = sum(list(children.values()))
        self.assertEqual(top_level_count,5)
        self.assertEqual(child_count,6)
        self.assertEqual(children["http://sbol_prefix.org/seq_1/1"],0)
        self.assertEqual(children["http://sbol_prefix.org/cd_1/1"],0)
        self.assertEqual(children["http://sbol_prefix.org/cd_2/1"],4)
        self.assertEqual(children["http://sbol_prefix.org/model_1/1"],0)
        self.assertEqual(children["http://sbol_prefix.org/mod_def_1/1"],2)

        max_depth,depths = get_depth(heirachy_tree)
        self.assertEqual(max_depth,1)
        self.assertEqual(depths["http://sbol_prefix.org/seq_1/1"],0)
        self.assertEqual(depths["http://sbol_prefix.org/cd_1/1"],0)
        self.assertEqual(depths["http://sbol_prefix.org/cd_2/1"],1)
        self.assertEqual(depths["http://sbol_prefix.org/model_1/1"],0)
        self.assertEqual(depths["http://sbol_prefix.org/mod_def_1/1"],1)

    def test_many_trees_many_levels(self):
        '''
        Test that runs many top-level objects BUT with only ONE relationship chain..
        Expect: All-Top-Level trees are one layer deep apart from one which is extremely deep.
        '''
        pass
    
    def test_many_trees_many_relationships_many_levels(self):
        '''
        Test that runs many top-level objects AND with many relationships AND many levels.
        The most invasive and complex test, essentially if this passes everything should pass.
        Expect: Each tree is atleast 3 layers deep with alteast three relationships.
        '''
        pass

    def test_sequence(self):
        '''
        Test Sequences with CD's to ensure that Sequences ARENT identified as children
        '''
        # Create SBOL from ShortBOL
        test_fn = "test_sequence.shb"
        return_code = shortbol_script_runner.parse_from_file(test_fn,optpaths=[lib_path],out=output_fn)
        self.assertEqual(list(return_code.keys())[0], "SBOL validator success.")
        test_graph = load_graph(output_fn)
        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),2)
        # Test get_tree
        heirachy_tree = generate_tree(roots,test_graph)
        SBOL2ShortBOL.tree_dump(heirachy_tree, os.path.join(output_dir,test_fn.split(".")[0] + ".txt"))

        self.common_tests(heirachy_tree,roots)

        # Bespoke tests that can only be done by knowledge of the graph.
        top_level_count,children = count_objects(heirachy_tree)
        child_count = sum(list(children.values()))
        self.assertEqual(top_level_count,2)
        self.assertEqual(child_count,0)
        self.assertEqual(children["http://sbol_prefix.org/seq_1/1"],0)
        self.assertEqual(children["http://sbol_prefix.org/pTetR/1"],0)

        max_depth,depths = get_depth(heirachy_tree)
        self.assertEqual(max_depth,0)
        self.assertEqual(depths["http://sbol_prefix.org/seq_1/1"],0)
        self.assertEqual(depths["http://sbol_prefix.org/pTetR/1"],0)


    def test_large_script(self):
        '''
        Tests a large script as almost like a user-test scenario.
        '''
        # Create SBOL from ShortBOL
        test_fn = "test_large_script.shb"
        return_code = shortbol_script_runner.parse_from_file(test_fn,optpaths=[lib_path],out=output_fn)
        self.assertEqual(list(return_code.keys())[0], "SBOL validator success.")
        test_graph = load_graph(output_fn)
        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),30)
        # Test get_tree
        heirachy_tree = generate_tree(roots,test_graph)
        SBOL2ShortBOL.tree_dump(heirachy_tree, os.path.join(output_dir,test_fn.split(".")[0] + ".txt"))

        self.common_tests(heirachy_tree,roots)
        # Bespoke tests that can only be done by knowledge of the graph.
        top_level_count,children = count_objects(heirachy_tree)
        child_count = sum(list(children.values()))
        self.assertEqual(top_level_count,30)
        self.assertEqual(child_count,76)
        self.assertEqual(children["http://sbol_prefix.org/Gal4VP16_gene/1"],3)
        self.assertEqual(children["http://sbol_prefix.org/EYFP_gene/1"],3)
        self.assertEqual(children["http://sbol_prefix.org/gRNA_b_gene/1"],5)   
        self.assertEqual(children["http://sbol_prefix.org/mKate_gene/1"],3)   
        self.assertEqual(children["http://sbol_prefix.org/cas9m_BFP_gene/1"],3)   
        self.assertEqual(children["http://sbol_prefix.org/CRISPR_Template/1"],15)   
        self.assertEqual(children["http://sbol_prefix.org/CRPb_characterization_Circuit/1"],44)   

        max_depth,depths = get_depth(heirachy_tree)
        self.assertEqual(max_depth,2)
        self.assertEqual(depths["http://sbol_prefix.org/Gal4VP16_gene/1"],1)
        self.assertEqual(depths["http://sbol_prefix.org/EYFP_gene/1"],1)
        self.assertEqual(depths["http://sbol_prefix.org/gRNA_b_gene/1"],1)   
        self.assertEqual(depths["http://sbol_prefix.org/mKate_gene/1"],1)   
        self.assertEqual(depths["http://sbol_prefix.org/cas9m_BFP_gene/1"],1)   
        self.assertEqual(depths["http://sbol_prefix.org/CRISPR_Template/1"],2)   
        self.assertEqual(depths["http://sbol_prefix.org/CRPb_characterization_Circuit/1"],2)  


    def test_large_script_2(self):
        '''
        Tests a large script as almost like a user-test scenario.
        '''
        # Create SBOL from ShortBOL
        test_fn = "test_large_script_2.shb"
        return_code = shortbol_script_runner.parse_from_file(test_fn,optpaths=[lib_path],out=output_fn)
        self.assertEqual(list(return_code.keys())[0], "SBOL validator success.")
        test_graph = load_graph(output_fn)
        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),4)
        # Test get_tree
        heirachy_tree = generate_tree(roots,test_graph)
        SBOL2ShortBOL.tree_dump(heirachy_tree, os.path.join(output_dir,test_fn.split(".")[0] + ".txt"))

        self.common_tests(heirachy_tree,roots)
        # Bespoke tests that can only be done by knowledge of the graph.
        top_level_count,children = count_objects(heirachy_tree)
        child_count = sum(list(children.values()))
        self.assertEqual(top_level_count,4)
        self.assertEqual(child_count,13)
        self.assertEqual(children["http://sbol_prefix.org/LacI_inverter/1"],8)
        self.assertEqual(children["http://sbol_prefix.org/TetR_inverter/1"],5)

        max_depth,depths = get_depth(heirachy_tree)
        self.assertEqual(max_depth,2)
        self.assertEqual(depths["http://sbol_prefix.org/LacI_inverter/1"],2)
        self.assertEqual(depths["http://sbol_prefix.org/TetR_inverter/1"],2)

    def test_non_shortbol_produced_1(self):
        '''
        All previous tests are made from ShortBOL produced SBOL.
        Should'nt make a difference but potentially some different ways of displaying SBOL.
        Genetic Toggle Switch
        '''
        # Create SBOL from ShortBOL
        test_fn = "test_non_shortbol_produced_1.rdf"
        return_code = SBOL2ShortBOL.general_validation(test_fn)
        self.assertTrue(return_code)
        test_graph = load_graph(test_fn)
        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),21)
        # Test get_tree
        heirachy_tree = generate_tree(roots,test_graph)
        SBOL2ShortBOL.tree_dump(heirachy_tree, os.path.join(output_dir,test_fn.split(".")[0] + ".txt"))

        self.common_tests(heirachy_tree,roots)
        # Bespoke tests that can only be done by knowledge of the graph.
        top_level_count,children = count_objects(heirachy_tree)
        child_count = sum(list(children.values()))
        self.assertEqual(top_level_count,21)
        self.assertEqual(child_count,54)

        max_depth,depths = get_depth(heirachy_tree)
        self.assertEqual(max_depth,2)
 

    def test_non_shortbol_produced_2(self):
        '''
        All previous tests are made from ShortBOL produced SBOL.
        Should'nt make a difference but potentially some different ways of displaying SBOL.
        ModuleDefinition
        '''
        # Create SBOL from ShortBOL
        test_fn = "test_non_shortbol_produced_2.rdf"
        return_code = SBOL2ShortBOL.general_validation(test_fn)
        self.assertTrue(return_code)
        test_graph = load_graph(test_fn)
        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),1)
        # Test get_tree
        heirachy_tree = generate_tree(roots,test_graph)
        SBOL2ShortBOL.tree_dump(heirachy_tree, os.path.join(output_dir,test_fn.split(".")[0] + ".txt"))

        self.common_tests(heirachy_tree,roots)
        # Bespoke tests that can only be done by knowledge of the graph.
        top_level_count,children = count_objects(heirachy_tree)
        child_count = sum(list(children.values()))
        self.assertEqual(top_level_count,1)
        self.assertEqual(child_count,5)
        self.assertEqual(children["http://sbolstandard.org/example/md/GFP_expression"],5)

        max_depth,depths = get_depth(heirachy_tree)
        self.assertEqual(max_depth,2)
        self.assertEqual(depths["http://sbolstandard.org/example/md/GFP_expression"],2)


    def test_non_shortbol_produced_3(self):
        '''
        All previous tests are made from ShortBOL produced SBOL.
        Should'nt make a difference but potentially some different ways of displaying SBOL.
        SequenceOutput
        '''
        # Create SBOL from ShortBOL
        test_fn = "test_non_shortbol_produced_3.rdf"
        return_code = SBOL2ShortBOL.general_validation(test_fn)
        self.assertTrue(return_code)
        test_graph = load_graph(test_fn)
        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),1)
        # Test get_tree
        heirachy_tree = generate_tree(roots,test_graph)
        SBOL2ShortBOL.tree_dump(heirachy_tree, os.path.join(output_dir,test_fn.split(".")[0] + ".txt"))

        self.common_tests(heirachy_tree,roots)
        # Bespoke tests that can only be done by knowledge of the graph.
        top_level_count,children = count_objects(heirachy_tree)
        child_count = sum(list(children.values()))
        self.assertEqual(top_level_count,1)
        self.assertEqual(child_count,0)
        self.assertEqual(children["http://partsregistry.org/seq/BBa_J23119"],0)

        max_depth,depths = get_depth(heirachy_tree)
        self.assertEqual(max_depth,0)
        self.assertEqual(depths["http://partsregistry.org/seq/BBa_J23119"],0)


    def test_non_shortbol_produced_4(self):
        '''
        All previous tests are made from ShortBOL produced SBOL.
        Should'nt make a difference but potentially some different ways of displaying SBOL.
        SequenceConstraintOutput
        '''
        # Create SBOL from ShortBOL
        test_fn = "test_non_shortbol_produced_4.rdf"
        return_code = SBOL2ShortBOL.general_validation(test_fn)
        self.assertTrue(return_code)
        test_graph = load_graph(test_fn)
        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),3)
        # Test get_tree
        heirachy_tree = generate_tree(roots,test_graph)
        SBOL2ShortBOL.tree_dump(heirachy_tree, os.path.join(output_dir,test_fn.split(".")[0] + ".txt"))

        self.common_tests(heirachy_tree,roots)
        # Bespoke tests that can only be done by knowledge of the graph.
        top_level_count,children = count_objects(heirachy_tree)
        child_count = sum(list(children.values()))
        self.assertEqual(top_level_count,3)
        self.assertEqual(child_count,3)
        self.assertEqual(children["http://partsregistry.org/cd/BBa_K174004"],3)
        self.assertEqual(children["http://partsregistry.org/cd/LacI_operator"],0)
        self.assertEqual(children["http://partsregistry.org/cd/pspac"],0)

        max_depth,depths = get_depth(heirachy_tree)
        self.assertEqual(max_depth,1)
        self.assertEqual(depths["http://partsregistry.org/cd/BBa_K174004"],1)
        self.assertEqual(depths["http://partsregistry.org/cd/LacI_operator"],0)
        self.assertEqual(depths["http://partsregistry.org/cd/pspac"],0)

    def test_non_shortbol_produced_5(self):
        '''
        All previous tests are made from ShortBOL produced SBOL.
        Should'nt make a difference but potentially some different ways of displaying SBOL.
        Moon
        '''
        # Create SBOL from ShortBOL
        test_fn = "test_non_shortbol_produced_5.rdf"
        return_code = SBOL2ShortBOL.general_validation(test_fn)
        self.assertTrue(return_code)
        test_graph = load_graph(test_fn)
        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),84)
        # Test get_tree
        heirachy_tree = generate_tree(roots,test_graph)
        SBOL2ShortBOL.tree_dump(heirachy_tree, os.path.join(output_dir,test_fn.split(".")[0] + ".txt"))

        self.common_tests(heirachy_tree,roots)
        # Bespoke tests that can only be done by knowledge of the graph.
        top_level_count,children = count_objects(heirachy_tree)
        child_count = sum(list(children.values()))
        self.assertEqual(top_level_count,84)
        self.assertEqual(child_count,283)

        max_depth,depths = get_depth(heirachy_tree)
        self.assertEqual(max_depth,2)


    def test_non_shortbol_produced_6(self):
        '''
        All previous tests are made from ShortBOL produced SBOL.
        Should'nt make a difference but potentially some different ways of displaying SBOL.
        ModuleDefinitionOutput
        '''
        # Create SBOL from ShortBOL
        test_fn = "test_non_shortbol_produced_6.rdf"
        return_code = SBOL2ShortBOL.general_validation(test_fn)
        self.assertTrue(return_code)
        test_graph = load_graph(test_fn)
        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),30)
        # Test get_tree
        heirachy_tree = generate_tree(roots,test_graph)
        SBOL2ShortBOL.tree_dump(heirachy_tree, os.path.join(output_dir,test_fn.split(".")[0] + ".txt"))

        self.common_tests(heirachy_tree,roots)
        # Bespoke tests that can only be done by knowledge of the graph.
        top_level_count,children = count_objects(heirachy_tree)
        child_count = sum(list(children.values()))
        self.assertEqual(top_level_count,30)
        self.assertEqual(child_count,52)

        max_depth,depths = get_depth(heirachy_tree)
        self.assertEqual(max_depth,2)

    def test_non_shortbol_produced_7(self):
        '''
        All previous tests are made from ShortBOL produced SBOL.
        Should'nt make a difference but potentially some different ways of displaying SBOL.
        ModelOutput
        '''
        # Create SBOL from ShortBOL
        test_fn = "test_non_shortbol_produced_7.rdf"
        return_code = SBOL2ShortBOL.general_validation(test_fn)
        self.assertTrue(return_code)
        test_graph = load_graph(test_fn)
        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),1)
        # Test get_tree
        heirachy_tree = generate_tree(roots,test_graph)
        SBOL2ShortBOL.tree_dump(heirachy_tree, os.path.join(output_dir,test_fn.split(".")[0] + ".txt"))

        self.common_tests(heirachy_tree,roots)
        # Bespoke tests that can only be done by knowledge of the graph.
        top_level_count,children = count_objects(heirachy_tree)
        child_count = sum(list(children.values()))
        self.assertEqual(top_level_count,1)
        self.assertEqual(child_count,0)

        max_depth,depths = get_depth(heirachy_tree)
        self.assertEqual(max_depth,0)

    def test_non_shortbol_produced_8(self):
        '''
        All previous tests are made from ShortBOL produced SBOL.
        Should'nt make a difference but potentially some different ways of displaying SBOL.
        GenericTopLevelOutput
        '''
        # Create SBOL from ShortBOL
        test_fn = "test_non_shortbol_produced_8.rdf"
        return_code = SBOL2ShortBOL.general_validation(test_fn)
        self.assertTrue(return_code)
        test_graph = load_graph(test_fn)
        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),1)
        # Test get_tree
        heirachy_tree = generate_tree(roots,test_graph)
        SBOL2ShortBOL.tree_dump(heirachy_tree, os.path.join(output_dir,test_fn.split(".")[0] + ".txt"))

        self.common_tests(heirachy_tree,roots)
        # Bespoke tests that can only be done by knowledge of the graph.
        top_level_count,children = count_objects(heirachy_tree)
        child_count = sum(list(children.values()))
        self.assertEqual(top_level_count,1)
        self.assertEqual(child_count,0)

        max_depth,depths = get_depth(heirachy_tree)
        self.assertEqual(max_depth,0)

    def test_non_shortbol_produced_9(self):
        '''
        All previous tests are made from ShortBOL produced SBOL.
        Should'nt make a difference but potentially some different ways of displaying SBOL.
        CutExample
        '''
        # Create SBOL from ShortBOL
        test_fn = "test_non_shortbol_produced_9.rdf"
        return_code = SBOL2ShortBOL.general_validation(test_fn)
        self.assertTrue(return_code)
        test_graph = load_graph(test_fn)
        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),2)
        # Test get_tree
        heirachy_tree = generate_tree(roots,test_graph)
        SBOL2ShortBOL.tree_dump(heirachy_tree, os.path.join(output_dir,test_fn.split(".")[0] + ".txt"))

        self.common_tests(heirachy_tree,roots)
        # Bespoke tests that can only be done by knowledge of the graph.
        top_level_count,children = count_objects(heirachy_tree)
        child_count = sum(list(children.values()))
        self.assertEqual(top_level_count,2)
        self.assertEqual(child_count,4)
        self.assertEqual(children["http://partsregistry.org/cd/BBa_J23119"],4)
        self.assertEqual(children["http://partsregistry.org/seq/BBa_J23119"],0)

        max_depth,depths = get_depth(heirachy_tree)
        self.assertEqual(max_depth,2)
        self.assertEqual(depths["http://partsregistry.org/cd/BBa_J23119"],2)
        self.assertEqual(depths["http://partsregistry.org/seq/BBa_J23119"],0)

    def test_non_shortbol_produced_10(self):
        '''
        All previous tests are made from ShortBOL produced SBOL.
        Should'nt make a difference but potentially some different ways of displaying SBOL.
        CollectionOutput
        '''
        # Create SBOL from ShortBOL
        test_fn = "test_non_shortbol_produced_10.rdf"
        return_code = SBOL2ShortBOL.general_validation(test_fn)
        self.assertTrue(return_code)
        test_graph = load_graph(test_fn)
        # Run GetRoots
        roots = SBOL2ShortBOL.find_graph_roots(test_graph)
        self.assertEqual(len(roots),1)
        # Test get_tree
        heirachy_tree = generate_tree(roots,test_graph)
        SBOL2ShortBOL.tree_dump(heirachy_tree, os.path.join(output_dir,test_fn.split(".")[0] + ".txt"))

        self.common_tests(heirachy_tree,roots)
        # Bespoke tests that can only be done by knowledge of the graph.
        top_level_count,children = count_objects(heirachy_tree)
        child_count = sum(list(children.values()))
        self.assertEqual(top_level_count,1)
        self.assertEqual(child_count,0)

        max_depth,depths = get_depth(heirachy_tree)
        self.assertEqual(max_depth,0)
    


def count_objects(heirachy_tree):
    children = {}
    branch_temp = []
    def count_objcets_inner(branches):
        for branch in branches:
            if isinstance(branch,dict) :
                branch_temp.append(1 + (max(map(count_objcets_inner, branch.values())) if branch else 0))
            else:
                pass
        if len(branch_temp) == 0:
            return 0
        return max(branch_temp)

    for top_level,branches in heirachy_tree.items():
        children[top_level] = count_objcets_inner(branches)
        branch_temp.clear()
    
    parents = len(list(heirachy_tree.keys()))
    return parents, children


def get_depth(heirachy_tree):
    depths = {}
    branch_temp = []
    def get_depth_inner(branches):
        def depth(d):
            if isinstance(d, dict):
                return 1 + (max(map(depth, d.values())) if d else 0)
            elif isinstance(d,list):
                return (max(map(depth, d)) if d else 0)
            return 0

        for branch in branches:
            branch_temp.append(depth(branch))

        if len(branch_temp) == 0:
            return 0
        else:
            return max(branch_temp)

    for top_level,branches in heirachy_tree.items():
        depths[top_level] = get_depth_inner(branches)
        branch_temp.clear()
    
    max_depth = max(list(depths.values()))
    return max_depth, depths


def load_graph(rdf_fn):
    test_graph = rdflib.Graph()
    test_graph.load(rdf_fn)
    return test_graph

def generate_tree(roots,graph):
    heirachy_tree = {}
    for root in roots:
        heirachy_tree[str(root[0])] = SBOL2ShortBOL.get_tree(graph,root[0])
    return heirachy_tree
import unittest
import rdflib
import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..','..',".."))
from run import parse_from_file
from shutil import copyfile

no_extension_output = "no_extension_output.xml"
extension_output = "extension_output_fn.xml"
templates = os.path.join("..", "..", "..","templates")
version = "sbol_2"


component_definition_type = rdflib.URIRef("http://sbols.org/v2#ComponentDefinition")
variant_type = rdflib.URIRef('http://sbols.org/v2#variant')
component_type = rdflib.URIRef('http://sbols.org/v2#component')
constraint_type =  rdflib.URIRef('http://sbols.org/v2#sequenceConstraint')
annotation_type =  rdflib.URIRef('http://sbols.org/v2#sequenceAnnotation')
template_type = rdflib.URIRef('http://sbols.org/v2#template')
variant_collection_type =   rdflib.URIRef('http://sbols.org/v2#member')

class CombinatorialDerivationTests(unittest.TestCase):

    def setUp(self):
        pass
    
    def tearDown(self):
        pass
        if os.path.isfile(no_extension_output):
            os.remove(no_extension_output)
        if os.path.isfile(extension_output):
           pass# os.remove(extension_output)
        if os.path.isfile("temporary_runner.shb"):
            os.remove("temporary_runner.shb")
        return super().tearDown()

    '''
    A test can be broken down as:
    Running the test file with and without the extension.
    Load both into graphs
    Run some generic tests
    Run custom tests.
    '''

    def test_combinatorial_derivation_single_variable_single_variant(self):
        test_fn = "test_combinatorial_derivation_1.shb"
        test_fn_with_extension = "test_combinatorial_derivation_1_extension.shb"

        extension_code = "@extension CombinatorialDerivation(cd_1)"
        
        return_code = parse_from_file(test_fn,"sbolxml",[templates],no_extension_output,[],version=version, no_validation=True)
        
        copyfile(test_fn, test_fn_with_extension)
        with open(test_fn_with_extension, 'a') as file:
            file.write("\n")
            file.write(extension_code)
        return_code = parse_from_file(test_fn_with_extension,"sbolxml",[templates],extension_output,[],version=version, no_validation=True)
        
        os.remove(test_fn_with_extension)

        no_extension_graph = rdflib.Graph()
        no_extension_graph.load(no_extension_output)
        extension_graph = rdflib.Graph()
        extension_graph.load(extension_output)

        # 1 variant produces 1 CD + 1 C 
        self.assertEqual(count_component_definitions(extension_graph),count_component_definitions(no_extension_graph) + count_variants(no_extension_graph))
        self.assertEqual(count_components(extension_graph),count_components(no_extension_graph) + count_variants(no_extension_graph))
        self.assertEqual(count_objects(extension_graph),count_objects(no_extension_graph))


        component_definitions = count_component_definitions_children(extension_graph)
        # Assert old CD's are unchanged
        component_definitions_no_extension = count_component_definitions_children(no_extension_graph)
        for k,v in component_definitions.items():
            if k in list(component_definitions_no_extension.keys()):
                self.assertDictEqual(v,component_definitions_no_extension[k])


        # Count test on new objects
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["components"],1)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["annotations"],0)


    def test_combinatorial_derivation_single_variable_double_variant(self):
        test_fn = "test_combinatorial_derivation_2.shb"
        test_fn_with_extension = "test_combinatorial_derivation_2_extension.shb"

        extension_code = "@extension CombinatorialDerivation(cd_1)"
        
        return_code = parse_from_file(test_fn,"sbolxml",[templates],no_extension_output,[],version=version, no_validation=True)
        
        copyfile(test_fn, test_fn_with_extension)
        with open(test_fn_with_extension, 'a') as file:
            file.write("\n")
            file.write(extension_code)
        return_code = parse_from_file(test_fn_with_extension,"sbolxml",[templates],extension_output,[],version=version, no_validation=True)
        
        os.remove(test_fn_with_extension)

        no_extension_graph = rdflib.Graph()
        no_extension_graph.load(no_extension_output)
        extension_graph = rdflib.Graph()
        extension_graph.load(extension_output)

        # 1 variant produces 1 CD + 1 C 
        self.assertEqual(count_component_definitions(extension_graph),count_component_definitions(no_extension_graph) + count_variants(no_extension_graph))
        self.assertEqual(count_components(extension_graph),count_components(no_extension_graph) + count_variants(no_extension_graph) * count_template_sub_components(no_extension_graph))
        


        component_definitions = count_component_definitions_children(extension_graph)
        # Assert old CD's are unchanged
        component_definitions_no_extension = count_component_definitions_children(no_extension_graph)
        for k,v in component_definitions.items():
            if k in list(component_definitions_no_extension.keys()):
                self.assertDictEqual(v,component_definitions_no_extension[k])


        # Count test on new objects
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["components"],1)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["annotations"],0)

        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["components"],1)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["annotations"],0)


    def test_combinatorial_derivation_single_variable_double_variant_multiple_components(self):
        test_fn = "test_combinatorial_derivation_3.shb"
        test_fn_with_extension = "test_combinatorial_derivation_3_extension.shb"

        extension_code = "@extension CombinatorialDerivation(combin_1)"
        
        return_code = parse_from_file(test_fn,"sbolxml",[templates],no_extension_output,[],version=version, no_validation=True)
        
        copyfile(test_fn, test_fn_with_extension)
        with open(test_fn_with_extension, 'a') as file:
            file.write("\n")
            file.write(extension_code)
        return_code = parse_from_file(test_fn_with_extension,"sbolxml",[templates],extension_output,[],version=version, no_validation=True)
        
        os.remove(test_fn_with_extension)

        no_extension_graph = rdflib.Graph()
        no_extension_graph.load(no_extension_output)
        extension_graph = rdflib.Graph()
        extension_graph.load(extension_output)

        # 1 variant produces 1 CD + 1 C 
        self.assertEqual(count_component_definitions(extension_graph),count_component_definitions(no_extension_graph) + count_variants(no_extension_graph))
        self.assertEqual(count_components(extension_graph),count_components(no_extension_graph) + count_variants(no_extension_graph) * count_template_sub_components(no_extension_graph))
        


        component_definitions = count_component_definitions_children(extension_graph)
        # Assert old CD's are unchanged
        component_definitions_no_extension = count_component_definitions_children(no_extension_graph)
        for k,v in component_definitions.items():
            if k in list(component_definitions_no_extension.keys()):
                self.assertDictEqual(v,component_definitions_no_extension[k])


        # Count test on new objects
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["components"],4)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["annotations"],0)

        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["components"],4)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["annotations"],0)


    def test_combinatorial_derivation_double_variable_double_variant_multiple_components(self):
        test_fn = "test_combinatorial_derivation_4.shb"
        test_fn_with_extension = "test_combinatorial_derivation_4_extension.shb"

        extension_code = "@extension CombinatorialDerivation(combin_1)"
        
        return_code = parse_from_file(test_fn,"sbolxml",[templates],no_extension_output,[],version=version, no_validation=True)
        
        copyfile(test_fn, test_fn_with_extension)
        with open(test_fn_with_extension, 'a') as file:
            file.write("\n")
            file.write(extension_code)
        return_code = parse_from_file(test_fn_with_extension,"sbolxml",[templates],extension_output,[],version=version, no_validation=True)
        
        os.remove(test_fn_with_extension)

        no_extension_graph = rdflib.Graph()
        no_extension_graph.load(no_extension_output)
        extension_graph = rdflib.Graph()
        extension_graph.load(extension_output)

        # 1 variant produces 1 CD + 1 C
        self.assertEqual(count_component_definitions(extension_graph),count_component_definitions(no_extension_graph) + count_variants(no_extension_graph))
        self.assertEqual(count_components(extension_graph),count_components(no_extension_graph) + count_variants(no_extension_graph) * count_template_sub_components(no_extension_graph))
        
        

        component_definitions = count_component_definitions_children(extension_graph)
        # Assert old CD's are unchanged
        component_definitions_no_extension = count_component_definitions_children(no_extension_graph)
        for k,v in component_definitions.items():
            if k in list(component_definitions_no_extension.keys()):
                self.assertDictEqual(v,component_definitions_no_extension[k])


        # Count test on new objects
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["components"],4)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["annotations"],0)

        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["components"],4)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["annotations"],0)


        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_1"]["variants"],0)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_1"]["components"],4)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_1"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_1"]["annotations"],0)

        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_2"]["variants"],0)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_2"]["components"],4)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_2"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_2"]["annotations"],0)


    def test_combinatorial_derivation_four_variable_double_variant_multiple_components(self):
        test_fn = "test_combinatorial_derivation_5.shb"
        test_fn_with_extension = "test_combinatorial_derivation_5_extension.shb"

        extension_code = "@extension CombinatorialDerivation(combin_1)"
        
        return_code = parse_from_file(test_fn,"sbolxml",[templates],no_extension_output,[],version=version, no_validation=True)
        
        copyfile(test_fn, test_fn_with_extension)
        with open(test_fn_with_extension, 'a') as file:
            file.write("\n")
            file.write(extension_code)
        return_code = parse_from_file(test_fn_with_extension,"sbolxml",[templates],extension_output,[],version=version, no_validation=True)
        
        os.remove(test_fn_with_extension)

        no_extension_graph = rdflib.Graph()
        no_extension_graph.load(no_extension_output)
        extension_graph = rdflib.Graph()
        extension_graph.load(extension_output)

        # 1 variant produces 1 CD + 1 C
        self.assertEqual(count_component_definitions(extension_graph),count_component_definitions(no_extension_graph) + count_variants(no_extension_graph))
        self.assertEqual(count_components(extension_graph),count_components(no_extension_graph) + count_variants(no_extension_graph) * count_template_sub_components(no_extension_graph))
        
        

        component_definitions = count_component_definitions_children(extension_graph)
        # Assert old CD's are unchanged
        component_definitions_no_extension = count_component_definitions_children(no_extension_graph)
        for k,v in component_definitions.items():
            if k in list(component_definitions_no_extension.keys()):
                self.assertDictEqual(v,component_definitions_no_extension[k])


        # Count test on new objects
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["components"],4)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["annotations"],0)

        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["components"],4)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["annotations"],0)


        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_1"]["variants"],0)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_1"]["components"],4)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_1"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_1"]["annotations"],0)

        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_2"]["variants"],0)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_2"]["components"],4)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_2"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_2"]["annotations"],0)


    def test_combinatorial_derivation_sequences(self):
        test_fn = "test_combinatorial_derivation_6.shb"
        test_fn_with_extension = "test_combinatorial_derivation_6_extension.shb"

        extension_code = "@extension CombinatorialDerivation(combin_1)"
        
        return_code = parse_from_file(test_fn,"sbolxml",[templates],no_extension_output,[],version=version, no_validation=True)
        
        copyfile(test_fn, test_fn_with_extension)
        with open(test_fn_with_extension, 'a') as file:
            file.write("\n")
            file.write(extension_code)
        return_code = parse_from_file(test_fn_with_extension,"sbolxml",[templates],extension_output,[],version=version, no_validation=True)
        
        os.remove(test_fn_with_extension)

        no_extension_graph = rdflib.Graph()
        no_extension_graph.load(no_extension_output)
        extension_graph = rdflib.Graph()
        extension_graph.load(extension_output)

        # 1 variant produces 1 CD + 1 C
        self.assertEqual(count_component_definitions(extension_graph),count_component_definitions(no_extension_graph) + count_variants(no_extension_graph))
        self.assertEqual(count_components(extension_graph),count_components(no_extension_graph) + count_variants(no_extension_graph) * count_template_sub_components(no_extension_graph))
        
        

        component_definitions = count_component_definitions_children(extension_graph)
        # Assert old CD's are unchanged
        component_definitions_no_extension = count_component_definitions_children(no_extension_graph)
        for k,v in component_definitions.items():
            if k in list(component_definitions_no_extension.keys()):
                self.assertDictEqual(v,component_definitions_no_extension[k])


        # Count test on new objects
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["components"],4)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["annotations"],0)

        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["components"],4)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["annotations"],0)


        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_1"]["variants"],0)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_1"]["components"],4)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_1"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_1"]["annotations"],0)

        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_2"]["variants"],0)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_2"]["components"],4)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_2"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_2"]["annotations"],0)


    def test_combinatorial_derivation_constraints(self):
        test_fn = "test_combinatorial_derivation_7.shb"
        test_fn_with_extension = "test_combinatorial_derivation_7_extension.shb"

        extension_code = "@extension CombinatorialDerivation(combin_1)"
        
        return_code = parse_from_file(test_fn,"sbolxml",[templates],no_extension_output,[],version=version, no_validation=True)
        
        copyfile(test_fn, test_fn_with_extension)
        with open(test_fn_with_extension, 'a') as file:
            file.write("\n")
            file.write(extension_code)
        return_code = parse_from_file(test_fn_with_extension,"sbolxml",[templates],extension_output,[],version=version, no_validation=True)
        
        os.remove(test_fn_with_extension)

        no_extension_graph = rdflib.Graph()
        no_extension_graph.load(no_extension_output)
        extension_graph = rdflib.Graph()
        extension_graph.load(extension_output)

        # 1 variant produces 1 CD + 1 C
        self.assertEqual(count_component_definitions(extension_graph),count_component_definitions(no_extension_graph) + count_variants(no_extension_graph))
        self.assertEqual(count_components(extension_graph),count_components(no_extension_graph) + count_variants(no_extension_graph) * count_template_sub_components(no_extension_graph))
        
        

        component_definitions = count_component_definitions_children(extension_graph)
        # Assert old CD's are unchanged
        component_definitions_no_extension = count_component_definitions_children(no_extension_graph)
        for k,v in component_definitions.items():
            if k in list(component_definitions_no_extension.keys()):
                self.assertDictEqual(v,component_definitions_no_extension[k])


        # Count test on new objects
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["components"],4)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["constraints"],3)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["annotations"],0)

        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["components"],4)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["constraints"],3)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["annotations"],0)


        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_1"]["variants"],0)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_1"]["components"],4)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_1"]["constraints"],3)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_1"]["annotations"],0)

        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_2"]["variants"],0)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_2"]["components"],4)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_2"]["constraints"],3)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_2"]["annotations"],0)


    def test_combinatorial_derivation_single_variable_four_variant_single_components_collection(self):
        test_fn = "test_combinatorial_derivation_8.shb"
        test_fn_with_extension = "test_combinatorial_derivation_8_extension.shb"

        extension_code = "@extension CombinatorialDerivation(combin_1)"
        
        return_code = parse_from_file(test_fn,"sbolxml",[templates],no_extension_output,[],version=version, no_validation=True)
        
        copyfile(test_fn, test_fn_with_extension)
        with open(test_fn_with_extension, 'a') as file:
            file.write("\n")
            file.write(extension_code)
        return_code = parse_from_file(test_fn_with_extension,"sbolxml",[templates],extension_output,[],version=version, no_validation=True)
        
        os.remove(test_fn_with_extension)

        no_extension_graph = rdflib.Graph()
        no_extension_graph.load(no_extension_output)
        extension_graph = rdflib.Graph()
        extension_graph.load(extension_output)

        # 1 variant produces 1 CD + 1 C
        self.assertEqual(count_component_definitions(extension_graph),count_component_definitions(no_extension_graph) + count_variants(no_extension_graph))
        self.assertEqual(count_components(extension_graph),count_components(no_extension_graph) + count_variants(no_extension_graph) * count_template_sub_components(no_extension_graph))
        
        

        component_definitions = count_component_definitions_children(extension_graph)
        # Assert old CD's are unchanged
        component_definitions_no_extension = count_component_definitions_children(no_extension_graph)
        for k,v in component_definitions.items():
            if k in list(component_definitions_no_extension.keys()):
                self.assertDictEqual(v,component_definitions_no_extension[k])


        # Count test on new objects
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["components"],1)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["annotations"],0)

        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["components"],1)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["annotations"],0)


        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_3"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_3"]["components"],1)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_3"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_3"]["annotations"],0)

        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_3"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_3"]["components"],1)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_3"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_3"]["annotations"],0)


    def test_combinatorial_derivation_single_variable_five_variant_single_components_collection_and_variant(self):
        test_fn = "test_combinatorial_derivation_9.shb"
        test_fn_with_extension = "test_combinatorial_derivation_9_extension.shb"

        extension_code = "@extension CombinatorialDerivation(combin_1)"
        
        return_code = parse_from_file(test_fn,"sbolxml",[templates],no_extension_output,[],version=version, no_validation=True)
        
        copyfile(test_fn, test_fn_with_extension)
        with open(test_fn_with_extension, 'a') as file:
            file.write("\n")
            file.write(extension_code)
        return_code = parse_from_file(test_fn_with_extension,"sbolxml",[templates],extension_output,[],version=version, no_validation=True)
        
        os.remove(test_fn_with_extension)

        no_extension_graph = rdflib.Graph()
        no_extension_graph.load(no_extension_output)
        extension_graph = rdflib.Graph()
        extension_graph.load(extension_output)

        # 1 variant produces 1 CD + 1 C
        self.assertEqual(count_component_definitions(extension_graph),count_component_definitions(no_extension_graph) + count_variants(no_extension_graph) - 1)
        self.assertEqual(count_components(extension_graph),count_components(no_extension_graph) + count_variants(no_extension_graph) * count_template_sub_components(no_extension_graph) - 1)
        
        

        component_definitions = count_component_definitions_children(extension_graph)
        # Assert old CD's are unchanged
        component_definitions_no_extension = count_component_definitions_children(no_extension_graph)
        for k,v in component_definitions.items():
            if k in list(component_definitions_no_extension.keys()):
                self.assertDictEqual(v,component_definitions_no_extension[k])


        # Count test on new objects
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["components"],1)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["annotations"],0)

        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["components"],1)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["annotations"],0)


        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_3"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_3"]["components"],1)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_3"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_3"]["annotations"],0)

        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_4"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_4"]["components"],1)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_4"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_4"]["annotations"],0)



    def test_combinatorial_derivation_single_variable_five_variant_single_components_double_collection(self):
        test_fn = "test_combinatorial_derivation_10.shb"
        test_fn_with_extension = "test_combinatorial_derivation_10_extension.shb"

        extension_code = "@extension CombinatorialDerivation(combin_1)"
        
        return_code = parse_from_file(test_fn,"sbolxml",[templates],no_extension_output,[],version=version, no_validation=True)
        
        copyfile(test_fn, test_fn_with_extension)
        with open(test_fn_with_extension, 'a') as file:
            file.write("\n")
            file.write(extension_code)
        return_code = parse_from_file(test_fn_with_extension,"sbolxml",[templates],extension_output,[],version=version, no_validation=True)
        
        os.remove(test_fn_with_extension)

        no_extension_graph = rdflib.Graph()
        no_extension_graph.load(no_extension_output)
        extension_graph = rdflib.Graph()
        extension_graph.load(extension_output)

        # 1 variant produces 1 CD + 1 C
        self.assertEqual(count_component_definitions(extension_graph),count_component_definitions(no_extension_graph) + count_variants(no_extension_graph))
        self.assertEqual(count_components(extension_graph),count_components(no_extension_graph) + count_variants(no_extension_graph) * count_template_sub_components(no_extension_graph))
        
        

        component_definitions = count_component_definitions_children(extension_graph)
        # Assert old CD's are unchanged
        component_definitions_no_extension = count_component_definitions_children(no_extension_graph)
        for k,v in component_definitions.items():
            if k in list(component_definitions_no_extension.keys()):
                self.assertDictEqual(v,component_definitions_no_extension[k])


        # Count test on new objects
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["components"],1)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["annotations"],0)

        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["components"],1)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["annotations"],0)


        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_3"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_3"]["components"],1)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_3"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_3"]["annotations"],0)

        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_3"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_3"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_3"]["annotations"],0)


    def test_combinatorial_derivation_annotation(self):
        test_fn = "test_combinatorial_derivation_11.shb"
        test_fn_with_extension = "test_combinatorial_derivation_11_extension.shb"

        extension_code = "@extension CombinatorialDerivation(combin_1)"
        
        return_code = parse_from_file(test_fn,"sbolxml",[templates],no_extension_output,[],version=version, no_validation=True)
        
        copyfile(test_fn, test_fn_with_extension)
        with open(test_fn_with_extension, 'a') as file:
            file.write("\n")
            file.write(extension_code)
        return_code = parse_from_file(test_fn_with_extension,"sbolxml",[templates],extension_output,[],version=version, no_validation=True)
        
        os.remove(test_fn_with_extension)

        no_extension_graph = rdflib.Graph()
        no_extension_graph.load(no_extension_output)
        extension_graph = rdflib.Graph()
        extension_graph.load(extension_output)

        # 1 variant produces 1 CD + 1 C
        self.assertEqual(count_component_definitions(extension_graph),count_component_definitions(no_extension_graph) + count_variants(no_extension_graph))
        self.assertEqual(count_components(extension_graph),count_components(no_extension_graph) + count_variants(no_extension_graph) * count_template_sub_components(no_extension_graph) + count_annotations(extension_graph) -4)
        
        

        component_definitions = count_component_definitions_children(extension_graph)
        # Assert old CD's are unchanged
        component_definitions_no_extension = count_component_definitions_children(no_extension_graph)
        for k,v in component_definitions.items():
            if k in list(component_definitions_no_extension.keys()):
                self.assertDictEqual(v,component_definitions_no_extension[k])


        # Count test on new objects
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["components"],4)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_1"]["annotations"],4)

        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["variants"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["components"],4)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_promoter_variable_1_promoter_variant_2"]["annotations"],4)


        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_1"]["variants"],0)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_1"]["components"],4)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_1"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_1"]["annotations"],4)

        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_2"]["variants"],0)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_2"]["components"],4)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_2"]["constraints"],0)
        self.assertEqual(component_definitions["template_1_rbs_variable_1_rbs_variant_2"]["annotations"],4)

def count_objects(graph):
    count = 0
    for s,p,o in graph:
        if p == rdflib.RDF.type:
            count = count + 1
    return count

def count_component_definitions(graph):
    count = 0
    for s,p,o in graph:
        if p == rdflib.RDF.type and o == component_definition_type:
            count = count + 1
    return count

def count_variants(graph):
    count = 0
    for s,p,o in graph:
        if p == variant_type:
            count = count + 1
        if p == variant_collection_type:
            count = count + 1
    return count

def count_components(graph):
    count = 0
    for s,p,o in graph:
        if p == component_type:
            count = count + 1
    return count

def count_annotations(graph):
    count = 0
    for s,p,o in graph:
        if p == annotation_type:
            count = count + 1
    return count

def count_component_definitions_children(graph):
    component_definitions = {}
    for s,p,o in graph:
        if o == component_definition_type:
            component_definitions[s.split("/")[-2]] = {"variants": 0,
                                        "components": 0,
                                        "constraints":0,
                                        "annotations":0,
                                        "misc":0
                                        }
    for s,p,o in graph:
        s = s.split("/")[-2]
        if s in list(component_definitions.keys()):
            if p == variant_type:
                component_definitions[s]["variants"] = component_definitions[s]["variants"] + 1
            elif p == component_type:
                component_definitions[s]["components"] = component_definitions[s]["components"] + 1
            elif p == constraint_type:
                component_definitions[s]["constraints"] = component_definitions[s]["constraints"] + 1
            elif p == annotation_type:
                component_definitions[s]["annotations"] = component_definitions[s]["annotations"] + 1
            else:
                component_definitions[s]["misc"] = component_definitions[s]["misc"] + 1

    return component_definitions

def count_template_sub_components(graph):
    count = 0
    templates = []
    for s,p,o in graph:
        if p == template_type:
            templates.append(o)
    
    for template in templates:
        for s,p,o in graph:
            if s == template and p == component_type:
                count = count + 1
    return count
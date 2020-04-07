
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

    def test_convert_simple(self):
        heirachy_tree = {
            'http://sbol_prefix.org/tetRInverter/1': [
            (rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter/1'), rdflib.term.URIRef('http://sbols.org/v2#persistentIdentity'), rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter')), 
            (rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter/1'), rdflib.term.URIRef('http://sbols.org/v2#type'), rdflib.term.URIRef('http://www.biopax.org/release/biopax-level3.owl#Dna')), 
            (rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter/1'), rdflib.term.URIRef('http://sbols.org/v2#version'), rdflib.term.Literal('1')), 
            (rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter/1'), rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdflib.term.URIRef('http://sbols.org/v2#ComponentDefinition')), 
            (rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter/1'), rdflib.term.URIRef('http://sbols.org/v2#name'), rdflib.term.Literal('name')), 
            (rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter/1'), rdflib.term.URIRef('http://sbols.org/v2#displayId'), rdflib.term.Literal('tetRInverter'))]
            ,'http://sbol_prefix.org/pTetR/1': [
                (rdflib.term.URIRef('http://sbol_prefix.org/pTetR/1'), rdflib.term.URIRef('http://sbols.org/v2#displayId'), rdflib.term.Literal('pTetR')), 
                (rdflib.term.URIRef('http://sbol_prefix.org/pTetR/1'), rdflib.term.URIRef('http://sbols.org/v2#type'), rdflib.term.URIRef('http://www.biopax.org/release/biopax-level3.owl#Dna')),
                (rdflib.term.URIRef('http://sbol_prefix.org/pTetR/1'), rdflib.term.URIRef('http://sbols.org/v2#persistentIdentity'), rdflib.term.URIRef('http://sbol_prefix.org/pTetR')), 
                (rdflib.term.URIRef('http://sbol_prefix.org/pTetR/1'), rdflib.term.URIRef('http://sbols.org/v2#role'), rdflib.term.URIRef('http://identifiers.org/so/SO:0000167')), 
                (rdflib.term.URIRef('http://sbol_prefix.org/pTetR/1'), rdflib.term.URIRef('http://sbols.org/v2#version'), rdflib.term.Literal('1')), 
                (rdflib.term.URIRef('http://sbol_prefix.org/pTetR/1'), rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdflib.term.URIRef('http://sbols.org/v2#ComponentDefinition'))]
        }
        shortbol_code = SBOL2ShortBOL.convert(heirachy_tree,lib_path)
        summary = summarise_shortbol_code(shortbol_code)
        self.assertEqual(summary['tetRInverter'], {'type': 'DNAComponent', 'parameters': [''], 'expansion': {'name': '"name"'}})
        self.assertEqual(summary['pTetR'], {'type': 'Promoter', 'parameters': [''], 'expansion': {}})


    def test_convert_intermediate(self):
        heirachy_tree = {
            'http://sbol_prefix.org/tetRInverter/1': [
                {'http://sbol_prefix.org/tetRInverter/pTetR_c/1': [
                    (rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter/pTetR_c/1'), rdflib.term.URIRef('http://sbols.org/v2#version'), rdflib.term.Literal('1')), 
                    (rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter/pTetR_c/1'), rdflib.term.URIRef('http://sbols.org/v2#access'), rdflib.term.URIRef('http://sbols.org/v2#public')), 
                    (rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter/pTetR_c/1'), rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdflib.term.URIRef('http://sbols.org/v2#Component')), 
                    (rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter/pTetR_c/1'), rdflib.term.URIRef('http://sbols.org/v2#displayId'), rdflib.term.Literal('pTetR_c')), 
                    (rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter/pTetR_c/1'), rdflib.term.URIRef('http://sbols.org/v2#persistentIdentity'), rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter/pTetR_c')), 
                    (rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter/pTetR_c/1'), rdflib.term.URIRef('http://sbols.org/v2#definition'), rdflib.term.URIRef('http://sbol_prefix.org/pTetR/1'))]
                }, 
                (rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter/1'), rdflib.term.URIRef('http://sbols.org/v2#persistentIdentity'), rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter')), 
                (rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter/1'), rdflib.term.URIRef('http://sbols.org/v2#type'), rdflib.term.URIRef('http://www.biopax.org/release/biopax-level3.owl#Dna')), 
                (rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter/1'), rdflib.term.URIRef('http://sbols.org/v2#version'), rdflib.term.Literal('1')), 
                (rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter/1'), rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdflib.term.URIRef('http://sbols.org/v2#ComponentDefinition')), 
                (rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter/1'), rdflib.term.URIRef('http://sbols.org/v2#component'), rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter/pTetR_c/1')), 
                (rdflib.term.URIRef('http://sbol_prefix.org/tetRInverter/1'), rdflib.term.URIRef('http://sbols.org/v2#displayId'), rdflib.term.Literal('tetRInverter'))]
            , 
            'http://sbol_prefix.org/pTetR/1': [
                (rdflib.term.URIRef('http://sbol_prefix.org/pTetR/1'), rdflib.term.URIRef('http://sbols.org/v2#displayId'), rdflib.term.Literal('pTetR')), 
                (rdflib.term.URIRef('http://sbol_prefix.org/pTetR/1'), rdflib.term.URIRef('http://sbols.org/v2#type'), rdflib.term.URIRef('http://www.biopax.org/release/biopax-level3.owl#Dna')),
                (rdflib.term.URIRef('http://sbol_prefix.org/pTetR/1'), rdflib.term.URIRef('http://sbols.org/v2#persistentIdentity'), rdflib.term.URIRef('http://sbol_prefix.org/pTetR')), 
                (rdflib.term.URIRef('http://sbol_prefix.org/pTetR/1'), rdflib.term.URIRef('http://sbols.org/v2#role'), rdflib.term.URIRef('http://identifiers.org/so/SO:0000167')), 
                (rdflib.term.URIRef('http://sbol_prefix.org/pTetR/1'), rdflib.term.URIRef('http://sbols.org/v2#version'), rdflib.term.Literal('1')), 
                (rdflib.term.URIRef('http://sbol_prefix.org/pTetR/1'), rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdflib.term.URIRef('http://sbols.org/v2#ComponentDefinition'))]
        }


        shortbol_code = SBOL2ShortBOL.convert(heirachy_tree,lib_path)
        summary = summarise_shortbol_code(shortbol_code)
        self.assertEqual(summary['tetRInverter'], {'type': 'DNAComponent', 'parameters': [''], 'expansion': {'component': 'pTetR_c'}})
        self.assertEqual(summary['pTetR'], {'type': 'Promoter', 'parameters': [''], 'expansion': {}})
        self.assertEqual(summary['pTetR_c'], {'type': 'Component', 'parameters': ['pTetR'], 'expansion': {}})
        



    def test_convert_advanced(self):
        heirachy_tree = {'http://sbol_prefix.org/LacI_inverter/1': [{'http://sbol_prefix.org/LacI_inverter/LacI_fc/1': [(rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacI_fc/1'), rdflib.term.URIRef('http://sbols.org/v2#access'), rdflib.term.URIRef('http://sbols.org/v2#public')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacI_fc/1'), rdflib.term.URIRef('http://sbols.org/v2#version'), rdflib.term.Literal('1')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacI_fc/1'), rdflib.term.URIRef('http://sbols.org/v2#displayId'), rdflib.term.Literal('LacI_fc')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacI_fc/1'), rdflib.term.URIRef('http://sbols.org/v2#definition'), rdflib.term.URIRef('http://sbol_prefix.org/LacI/1')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacI_fc/1'), rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdflib.term.URIRef('http://sbols.org/v2#FunctionalComponent')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacI_fc/1'), rdflib.term.URIRef('http://sbols.org/v2#persistentIdentity'), rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacI_fc')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacI_fc/1'), rdflib.term.URIRef('http://sbols.org/v2#direction'), rdflib.term.URIRef('http://sbols.org/v2#none'))]}, {'http://sbol_prefix.org/LacI_inverter/LacITetR_int/1': [{'http://sbol_prefix.org/LacI_inverter/LacITetR_int/TetR_lacinv_part/1': [(rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/TetR_lacinv_part/1'), rdflib.term.URIRef('http://sbols.org/v2#persistentIdentity'), rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/TetR_lacinv_part')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/TetR_lacinv_part/1'), rdflib.term.URIRef('http://sbols.org/v2#participant'), rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/TetR_fc/1')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/TetR_lacinv_part/1'), rdflib.term.URIRef('http://sbols.org/v2#version'), rdflib.term.Literal('1')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/TetR_lacinv_part/1'), rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdflib.term.URIRef('http://sbols.org/v2#Participation')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/TetR_lacinv_part/1'), rdflib.term.URIRef('http://sbols.org/v2#role'), rdflib.term.URIRef('http://identifiers.org/biomodels.sbo/SBO:0000642')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/TetR_lacinv_part/1'), rdflib.term.URIRef('http://sbols.org/v2#displayId'), rdflib.term.Literal('TetR_lacinv_part'))]}, {'http://sbol_prefix.org/LacI_inverter/LacITetR_int/LacI_lacinv_part/1': [(rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/LacI_lacinv_part/1'), rdflib.term.URIRef('http://sbols.org/v2#version'), rdflib.term.Literal('1')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/LacI_lacinv_part/1'), rdflib.term.URIRef('http://sbols.org/v2#persistentIdentity'), rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/LacI_lacinv_part')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/LacI_lacinv_part/1'), rdflib.term.URIRef('http://sbols.org/v2#role'), rdflib.term.URIRef('http://identifiers.org/biomodels.sbo/SBO:0000020')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/LacI_lacinv_part/1'), rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdflib.term.URIRef('http://sbols.org/v2#Participation')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/LacI_lacinv_part/1'), rdflib.term.URIRef('http://sbols.org/v2#participant'), rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacI_fc/1')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/LacI_lacinv_part/1'), rdflib.term.URIRef('http://sbols.org/v2#displayId'), rdflib.term.Literal('LacI_lacinv_part'))]}, (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/1'), rdflib.term.URIRef('http://sbols.org/v2#type'), rdflib.term.URIRef('http://sbol_prefix.org/inhibition')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/1'), rdflib.term.URIRef('http://sbols.org/v2#persistentIdentity'), rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/1'), rdflib.term.URIRef('http://sbols.org/v2#version'), rdflib.term.Literal('1')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/1'), rdflib.term.URIRef('http://sbols.org/v2#participation'), rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/TetR_lacinv_part/1')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/1'), rdflib.term.URIRef('http://sbols.org/v2#displayId'), rdflib.term.Literal('LacITetR_int')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/1'), rdflib.term.URIRef('http://sbols.org/v2#participation'), rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/LacI_lacinv_part/1')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/1'), rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdflib.term.URIRef('http://sbols.org/v2#Interaction'))]}, {'http://sbol_prefix.org/LacI_inverter/TetR_fc/1': [(rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/TetR_fc/1'), rdflib.term.URIRef('http://sbols.org/v2#direction'), rdflib.term.URIRef('http://sbols.org/v2#none')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/TetR_fc/1'), rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdflib.term.URIRef('http://sbols.org/v2#FunctionalComponent')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/TetR_fc/1'), rdflib.term.URIRef('http://sbols.org/v2#version'), rdflib.term.Literal('1')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/TetR_fc/1'), rdflib.term.URIRef('http://sbols.org/v2#persistentIdentity'), rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/TetR_fc')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/TetR_fc/1'), rdflib.term.URIRef('http://sbols.org/v2#access'), rdflib.term.URIRef('http://sbols.org/v2#public')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/TetR_fc/1'), rdflib.term.URIRef('http://sbols.org/v2#definition'), rdflib.term.URIRef('http://sbol_prefix.org/TetR/1')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/TetR_fc/1'), rdflib.term.URIRef('http://sbols.org/v2#displayId'), rdflib.term.Literal('TetR_fc'))]}, (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/1'), rdflib.term.URIRef('http://sbols.org/v2#persistentIdentity'), rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/1'), rdflib.term.URIRef('http://sbols.org/v2#displayId'), rdflib.term.Literal('LacI_inverter')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/1'), rdflib.term.URIRef('http://sbols.org/v2#functionalComponent'), rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/TetR_fc/1')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/1'), rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdflib.term.URIRef('http://sbols.org/v2#ModuleDefinition')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/1'), rdflib.term.URIRef('http://sbols.org/v2#interaction'), rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacITetR_int/1')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/1'), rdflib.term.URIRef('http://sbols.org/v2#version'), rdflib.term.Literal('1')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/1'), rdflib.term.URIRef('http://sbols.org/v2#functionalComponent'), rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/LacI_fc/1')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI_inverter/1'), rdflib.term.URIRef('http://purl.org/dc/terms/description'), rdflib.term.Literal('LacI inverter'))], 'http://sbol_prefix.org/TetR/1': [(rdflib.term.URIRef('http://sbol_prefix.org/TetR/1'), rdflib.term.URIRef('http://sbols.org/v2#persistentIdentity'), rdflib.term.URIRef('http://sbol_prefix.org/TetR')), (rdflib.term.URIRef('http://sbol_prefix.org/TetR/1'), rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdflib.term.URIRef('http://sbols.org/v2#ComponentDefinition')), (rdflib.term.URIRef('http://sbol_prefix.org/TetR/1'), rdflib.term.URIRef('http://sbols.org/v2#version'), rdflib.term.Literal('1')), (rdflib.term.URIRef('http://sbol_prefix.org/TetR/1'), rdflib.term.URIRef('http://sbols.org/v2#displayId'), rdflib.term.Literal('TetR')), (rdflib.term.URIRef('http://sbol_prefix.org/TetR/1'), rdflib.term.URIRef('http://sbols.org/v2#type'), rdflib.term.URIRef('http://www.biopax.org/release/biopax-level3.owl#Protein'))], 'http://sbol_prefix.org/LacI/1': [(rdflib.term.URIRef('http://sbol_prefix.org/LacI/1'), rdflib.term.URIRef('http://sbols.org/v2#version'), rdflib.term.Literal('1')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI/1'), rdflib.term.URIRef('http://sbols.org/v2#displayId'), rdflib.term.Literal('LacI')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI/1'), rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdflib.term.URIRef('http://sbols.org/v2#ComponentDefinition')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI/1'), rdflib.term.URIRef('http://sbols.org/v2#type'), rdflib.term.URIRef('http://www.biopax.org/release/biopax-level3.owl#Protein')), (rdflib.term.URIRef('http://sbol_prefix.org/LacI/1'), rdflib.term.URIRef('http://sbols.org/v2#persistentIdentity'), rdflib.term.URIRef('http://sbol_prefix.org/LacI'))]}
        
        shortbol_code = SBOL2ShortBOL.convert(heirachy_tree,lib_path)
        summary = summarise_shortbol_code(shortbol_code)
        self.assertEqual(summary['TetR'], {'type': 'ProteinComponent', 'parameters': [''], 'expansion': {}})
        self.assertEqual(summary['LacI'], {'type': 'ProteinComponent', 'parameters': [''], 'expansion': {}})

        self.assertEqual(summary['TetR_fc'], {'type': 'NoneComponent', 'parameters': ['TetR'], 'expansion': {}})
        self.assertEqual(summary['LacI_fc'], {'type': 'NoneComponent', 'parameters': ['LacI'], 'expansion': {}})
        self.assertEqual(summary['LacI_lacinv_part'], {'type': 'Inhibitor', 'parameters': ['LacI_fc'], 'expansion': {}})
        self.assertEqual(summary['TetR_lacinv_part'], {'type': 'Inhibited', 'parameters': ['TetR_fc'], 'expansion': {}})
        self.assertEqual(summary['LacITetR_int'], {'type': 'Interaction', 'parameters': ['inhibition'], 'expansion': {'participation':'TetR_lacinv_part','participation':'LacI_lacinv_part'}})
        self.assertEqual(summary['LacI_inverter'], {'type': 'ModuleDefinition', 'parameters': [''], 'expansion': {'description':'"LacIinverter"',
                                                                                                                  "functionalComponent" : "TetR_fc", 
                                                                                                                  "functionalComponent" : "LacI_fc",
                                                                                                                  "interaction" : "LacITetR_int"}})


def summarise_shortbol_code(shb_code):
    is_a = "is a"
    lines = shb_code.split("\n")
    index = 0
    templates = {}
    name = ""
    type = ""
    parameters = []
    expansion = {}
    while index != len(lines):
    
        if is_a in lines[index]:
            name = lines[index].split(is_a)[0].replace(" ","")
            type = lines[index].split(is_a)[1].split("(")[0].replace(" ","")
            parameters = lines[index].split(is_a)[1].split("(")[1].replace(")","").split(",")

            if index + 1 < len(lines) and lines[index + 1] == "(":
                while lines[index] != ")":
                    if "=" in lines[index]:
                        l = lines[index].replace(" ","")
                        expansion[l.split("=")[0]] = l.split("=")[1]
                    index = index + 1


            templates[name] = {"type":type,
                                "parameters":parameters,
                                "expansion":expansion }
            name = ""
            type = ""
            parameters = []
            expansion = {}
        index = index + 1
    return templates

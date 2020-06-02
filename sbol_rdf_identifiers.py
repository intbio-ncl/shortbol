import rdflib
from rdfscript.core import Uri 

class SBOLIdentifiers:
    def __init__(self):
        self.namespaces = SBOL2Namespace()
        self.objects = SBOL2Objects(self.namespaces)
        self.predicates = SBOL2Predicates(self.namespaces)
        self.external = SBOL2ExternalIdentifiers(self.namespaces)
    
    def swap_version(self, version):
        if version == "sbol_3":
            self.namespaces = SBOL3Namespace()
            self.objects = SBOL3Objects(self.namespaces)
            self.predicates = SBOL3Predicates(self.namespaces)
            self.external = SBOL3ExternalIdentifiers(self.namespaces)
    
class SBOL2Namespace:
    def __init__(self):
        self.sbol = Uri('http://sbols.org/v2#')
        identifiers = Uri('http://identifiers.org/')
        self.sequence_ontology = Uri(identifiers + Uri('so/SO:'))
        self.sbo_biomodels = Uri(identifiers + Uri('biomodels.sbo/SBO:'))
        self.identifier_edam = Uri(identifiers + Uri('edam/'))

        self.biopax = Uri('http://www.biopax.org/release/biopax-level3.owl#')
        self.dc = Uri('http://purl.org/dc/terms/')
        self.edam = Uri('http://edamontology.org/format')
        self.owl = Uri('http://www.w3.org/2002/07/owl#')
        self.prov = Uri('https://www.w3.org/ns/prov#')

class SBOL2Objects:
    def __init__(self, namespaces):
        self.namespaces = namespaces
        self.component_definition = Uri(self.namespaces.sbol + Uri('ComponentDefinition'))
        self.component = Uri(self.namespaces.sbol + Uri('Component'))
        self.module_definition = Uri(self.namespaces.sbol + Uri('ModuleDefinition'))
        self.range = Uri(self.namespaces.sbol + Uri('Range'))
        self.cut = Uri(self.namespaces.sbol + Uri('Cut'))
        self.sequence = Uri(self.namespaces.sbol + Uri("Sequence"))
        self.combinatorial_derivation = Uri(self.namespaces.sbol + Uri("CombinatorialDerivation"))
        self.experiment = Uri(self.namespaces.sbol + Uri("Experiment"))
        self.experimental_data = Uri(self.namespaces.sbol + Uri("ExperimentalData"))
        self.functional_component = Uri(self.namespaces.sbol + Uri("FunctionalComponent"))
        self.sequence = Uri(self.namespaces.sbol + Uri("Sequence"))
        self.implementation = Uri(self.namespaces.sbol + Uri("Implementation"))
        self.interaction = Uri(self.namespaces.sbol + Uri("Interaction"))
        self.generic_location = Uri(self.namespaces.sbol + Uri("GenericLocation"))
        self.mapsTo = Uri(self.namespaces.sbol + Uri("MapsTo"))
        self.module = Uri(self.namespaces.sbol + Uri("Module"))
        self.model = Uri(self.namespaces.sbol + Uri("Model"))
        self.attachment = Uri(self.namespaces.sbol + Uri("Attachment"))
        self.collection = Uri(self.namespaces.sbol + Uri("Collection"))
        self.sequence_annotation = Uri(self.namespaces.sbol + Uri("SequenceAnnotation"))

        self.top_levels = {Uri(self.namespaces.sbol + Uri(name)) for name in
                        ['Sequence',
                        'ComponentDefinition',
                        'ModuleDefinition',
                        'Model',
                        'Collection',
                        'GenericTopLevel',
                        'Attachment',
                        'Activity',
                        'Agent',
                        'Plan',
                        'Implementation',
                        'CombinatorialDerivation',
                        'Experiment',
                        'ExperimentalData']}

class SBOL2Predicates:
    def __init__(self, namespaces):
        self.namespaces = namespaces
        self.rdf_type = Uri(rdflib.RDF.type)

        self.display_id = Uri(self.namespaces.sbol + Uri('displayId'))
        self.persistent_identity = Uri(self.namespaces.sbol + Uri('persistentIdentity'))
        self.version = Uri(self.namespaces.sbol + Uri('version'))


        self.component = Uri(self.namespaces.sbol + Uri('component'))
        self.functional_component = Uri(self.namespaces.sbol + Uri('functionalComponent'))
        self.sequence_annotation = Uri(self.namespaces.sbol + Uri('sequenceAnnotation'))
        self.sequence_constraint = Uri(self.namespaces.sbol + Uri('sequenceConstraint'))
        self.location = Uri(self.namespaces.sbol + Uri('location'))
        self.sequence = Uri(self.namespaces.sbol + Uri('sequence'))
        self.cut = Uri(self.namespaces.sbol + Uri('cut'))
        self.at = Uri(self.namespaces.sbol + Uri('at'))

        self.definition = Uri(self.namespaces.sbol + Uri('definition'))
        self.sequence_constraint_restriction = Uri(self.namespaces.sbol + Uri('restriction'))
        self.sequence_constraint_subject = Uri(self.namespaces.sbol + Uri('subject'))
        self.sequence_constraint_object = Uri(self.namespaces.sbol + Uri('object'))
        self.type = Uri(self.namespaces.sbol + Uri('type'))
        self.role = Uri(self.namespaces.sbol + Uri('role'))
        self.start = Uri(self.namespaces.sbol + Uri('start'))
        self.end = Uri(self.namespaces.sbol + Uri('end'))

        self.interaction = Uri(self.namespaces.sbol + Uri('interaction'))
        self.participation = Uri(self.namespaces.sbol + Uri('participation'))
        self.elements = Uri(self.namespaces.sbol + Uri('elements'))
        self.participant = Uri(self.namespaces.sbol + Uri('participant'))
        self.encoding = Uri(self.namespaces.sbol + Uri('encoding'))
        self.direction = Uri(self.namespaces.sbol + Uri('direction'))
        self.access = Uri(self.namespaces.sbol + Uri('access'))

        self.template = Uri(self.namespaces.sbol + Uri('template'))
        self.variable_component = Uri(self.namespaces.sbol + Uri('variableComponent'))
        self.variable = Uri(self.namespaces.sbol + Uri("variable"))
        self.variant = Uri(self.namespaces.sbol + Uri("variant"))
        self.variant_collection = Uri(self.namespaces.sbol + Uri("variantCollection"))
        self.member = Uri(self.namespaces.sbol + Uri("member"))
        self.public = Uri(self.namespaces.sbol + Uri("public"))


        
        self.ownership_predicates = {Uri(self.rdf_type + Uri(predicate)) for predicate in
                                ['module',
                                'mapsTo',
                                'interaction',
                                'participation',
                                'functionalComponent',
                                'sequenceConstraint',
                                'location',
                                'sequenceAnnotation',
                                'variableComponent']}  

class SBOL2ExternalIdentifiers:
    def __init__(self, namespaces):
        self.namespaces = namespaces

        self.component_definition_DNA = Uri(self.namespaces.biopax + Uri("Dna"))
        self.component_definition_DNARegion = Uri(self.namespaces.biopax + Uri("DnaRegion"))
        self.component_definition_RNA = Uri(self.namespaces.biopax + Uri("Rna"))
        self.component_definition_RNARegion = Uri(self.namespaces.biopax + Uri("RnaRegion"))
        self.component_definition_protein = Uri(self.namespaces.biopax + Uri("Protein"))
        self.component_definition_smallMolecule = Uri(self.namespaces.biopax + Uri("SmallMolecule"))
        self.component_definition_complex = Uri(self.namespaces.biopax + Uri("Complex"))

        self.component_definition_promoter       = Uri(self.namespaces.sequence_ontology + Uri("0000167"))
        self.component_definition_rbs            = Uri(self.namespaces.sequence_ontology + Uri("0000139"))
        self.component_definition_cds            = Uri(self.namespaces.sequence_ontology + Uri("0000316"))
        self.component_definition_terminator     = Uri(self.namespaces.sequence_ontology + Uri("0000141"))
        self.component_definition_gene           = Uri(self.namespaces.sequence_ontology + Uri("0000704"))
        self.component_definition_operator       = Uri(self.namespaces.sequence_ontology + Uri("0000057"))
        self.component_definition_engineeredGene = Uri(self.namespaces.sequence_ontology + Uri("0000280"))
        self.component_definition_mRNA           = Uri(self.namespaces.sequence_ontology + Uri("0000234"))
        self.component_definition_engineeredRegion = Uri(self.namespaces.sequence_ontology + Uri("0000804"))
        self.component_definition_nonCovBindingSite = Uri(self.namespaces.sequence_ontology + Uri("0001091"))
        self.component_definition_effector       = Uri("http://identifiers.org/chebi/CHEBI:35224")
        self.component_definition_startCodon     = Uri(self.namespaces.sequence_ontology + Uri("0000318"))
        self.component_definition_tag            = Uri(self.namespaces.sequence_ontology + Uri("0000324"))
        self.component_definition_engineeredTag  = Uri(self.namespaces.sequence_ontology + Uri("0000807"))
        self.component_definition_sgRNA          = Uri(self.namespaces.sequence_ontology + Uri("0001998"))
        self.component_definition_transcriptionFactor = Uri("ttp://identifiers.org/go/GO:0003700")

        self.interaction_inhibition = Uri(self.namespaces.sbo_biomodels + Uri("0000169"))
        self.interaction_stimulation = Uri(self.namespaces.sbo_biomodels + Uri("0000170"))
        self.interaction_biochemical_reaction = Uri(self.namespaces.sbo_biomodels + Uri("0000176"))
        self.interaction_noncovalent_bonding = Uri(self.namespaces.sbo_biomodels + Uri("0000177"))
        self.interaction_degradation = Uri(self.namespaces.sbo_biomodels + Uri("0000179"))
        self.interaction_genetic_production = Uri(self.namespaces.sbo_biomodels + Uri("0000589"))
        self.interaction_control = Uri(self.namespaces.sbo_biomodels + Uri("0000168"))

        self.participant_inhibitor = Uri(self.namespaces.sbo_biomodels + Uri("0000020"))
        self.participant_inhibited = Uri(self.namespaces.sbo_biomodels + Uri("0000642"))
        self.participant_stimulator =  Uri(self.namespaces.sbo_biomodels + Uri("0000459"))
        self.participant_stimulated = Uri(self.namespaces.sbo_biomodels + Uri("0000643"))
        self.participant_modifier = Uri(self.namespaces.sbo_biomodels + Uri("0000019"))
        self.participant_modified = Uri(self.namespaces.sbo_biomodels + Uri("0000644"))
        self.participant_product = Uri(self.namespaces.sbo_biomodels + Uri("0000011"))
        self.participant_reactant = Uri(self.namespaces.sbo_biomodels + Uri("0000010"))
        self.participant_participation_promoter = Uri(self.namespaces.sbo_biomodels + Uri("0000598")) 
        self.participant_template = Uri(self.namespaces.sbo_biomodels + Uri("0000645"))

        self.location_orientation_inline = Uri(self.namespaces.sbol + Uri("inline"))
        self.location_orientation_reverseComplement = Uri(self.namespaces.sbol + Uri("reverseComplement"))

        self.functional_component_direction_in = Uri(self.namespaces.sbol + Uri("in"))
        self.functional_component_direction_out = Uri(self.namespaces.sbol + Uri("out"))
        self.functional_component_direction_inout = Uri(self.namespaces.sbol + Uri("inout")) 
        self.functional_component_direction_none = Uri(self.namespaces.sbol + Uri("none"))

        self.sequence_encoding_iupacDNA = Uri("http://www.chem.qmul.ac.uk/iubmb/misc/naseq.html")
        self.sequence_encoding_iupacRNA = Uri("http://www.chem.qmul.ac.uk/iubmb/misc/naseq.html")
        self.sequence_encoding_iupacProtein = Uri("http://www.chem.qmul.ac.uk/iupac/AminoAcid/")
        self.sequence_encoding_opensmilesSMILES = Uri("http://www.opensmiles.org/opensmiles.html")

        self.sequence_constraint_restriction_precedes = Uri(self.namespaces.sbol + Uri("precedes"))
        self.sequence_constraint_restriction_sameOrientationAs = Uri(self.namespaces.sbol + Uri("sameOrientationAs"))
        self.sequence_constraint_restriction_oppositeOrientationAs = Uri(self.namespaces.sbol + Uri("oppositeOrientationAs"))
        self.sequence_constraint_restriction_differentFrom = Uri(self.namespaces.sbol + Uri("differentFrom"))

        self.model_language_SBML = Uri(self.namespaces.edam + Uri("format_2585"))
        self.model_language_CellML = Uri(self.namespaces.edam + Uri("format_3240"))
        self.model_language_BioPAX = Uri(self.namespaces.edam + Uri("format_3156"))

        self.model_framework_continuous =  Uri(self.namespaces.sbol + Uri("0000062"))
        self.model_framework_discrete = Uri(self.namespaces.sbol + Uri("0000063"))

        self.mapsTo_refinement_useRemote = Uri(self.namespaces.sbol + Uri("useRemote"))
        self.mapsTo_refinement_useLocal = Uri(self.namespaces.sbol + Uri("useLocal")) 
        self.mapsTo_refinement_verifyIdentical  = Uri(self.namespaces.sbol + Uri("verifyIdentical"))
        self.mapsTo_refinement_merge = Uri(self.namespaces.sbol + Uri("merge")) 

        self.variable_component_cardinality_zeroOrOne = Uri(self.namespaces.sbol + Uri("zeroOrOne")) 
        self.variable_component_cardinality_one = Uri(self.namespaces.sbol + Uri("one"))
        self.variable_component_cardinality_zeroOrMore = Uri(self.namespaces.sbol + Uri("zeroOrMore"))
        self.variable_component_cardinality_oneOrMore = Uri(self.namespaces.sbol + Uri("oneOrMore"))


        self.dna_roles = {self.component_definition_promoter : "Promoter",
                        self.component_definition_rbs : "RBS",
                        self.component_definition_cds : "CDS",
                        self.component_definition_terminator : "Terminator",
                        self.component_definition_engineeredRegion : "Engineered Region",
                        self.component_definition_engineeredRegion : "Engineered Region",
                        self.component_definition_operator : "Operator",
                        self.component_definition_gene : "Gene"}
        self.rna_roles = {self.component_definition_mRNA : "mRNA",
                         self.component_definition_sgRNA : "sgRNA",
                         self.component_definition_cds : "CDS RNA"}
        self.protein_roles = {self.component_definition_transcriptionFactor : "Transcriptional Factor"}
        self.small_molecule_roles = {self.component_definition_effector : "Effector"}
        self.complex_roles = {}

    def get_component_definition_identifier_name(self, type,role = None):
        '''
        Reverse method that when you know the URI's return a descriptive name for said ComponentDefinition
        '''
        if type == self.component_definition_DNA or type == self.component_definition_DNARegion:
            try:
                return self.dna_roles[role]
            except KeyError:
                return "DNA"

        elif type == self.component_definition_RNA or type == self.component_definition_RNARegion:
            try:
                return self.rna_roles[role]
            except KeyError:
                return "RNA"

        elif type == self.component_definition_protein:
            try:
                return self.protein_roles[role]
            except KeyError:
                return "Protein"

        elif type == self.component_definition_smallMolecule:
            try:
                return self.small_molecule_roles[role]
            except KeyError:
                return "Small Molecule"

        elif type == self.component_definition_complex:
            try:
                return self.complex_roles[role]
            except KeyError:
                return "Complex"

        else:
            return "Unknown"
        return "Unknown"
    
    def get_type_from_role(self,role):
        if role in self.dna_roles:
            return self.component_definition_DNA
        if role in self.rna_roles:
            return self.component_definition_RNA
        if role in self.protein_roles:
            return self.component_definition_protein
        if role in self.small_molecule_roles:
            return self.component_definition_smallMolecule
        if role in self.complex_roles:
            return self.component_definition_complex



class SBOL3Namespace:
    def __init__(self):
        self.sbol = Uri('http://sbols.org/v3#')
        identifiers = Uri('http://identifiers.org/')
        self.sequence_ontology = Uri(identifiers + Uri('so/SO:'))
        self.sbo_biomodels = Uri(identifiers + Uri('biomodels.sbo/SBO:'))
        self.identifier_edam = Uri(identifiers + Uri('edam/'))

        self.biopax = Uri('http://www.biopax.org/release/biopax-level3.owl#')
        self.dc = Uri('http://purl.org/dc/terms/')
        self.edam = Uri('http://edamontology.org/format')
        self.owl = Uri('http://www.w3.org/2002/07/owl#')
        self.prov = Uri('https://www.w3.org/ns/prov#')


class SBOL3Objects:
    def __init__(self, namespaces):
        self.namespaces = namespaces

        self.top_levels = {Uri(self.namespaces.sbol + Uri(name)) for name in
             ['Sequence',
              'Component',
              'Model',
              'Collection',
              'Attachment',
              'Implementation',
              'CombinatorialDerivation',
              'Experiment',
              'ExperimentalData']}

class SBOL3Predicates:
    def __init__(self, namespaces):
        self.namespaces = namespaces
        self.rdf_type = Uri(rdflib.RDF.type)

        self.display_id = Uri(self.namespaces.sbol + Uri('displayId'))
        self.persistent_identity = Uri(self.namespaces.sbol + Uri('persistentIdentity'))
        self.version = Uri(self.namespaces.sbol + Uri('version'))



class SBOL3ExternalIdentifiers:
    def __init__(self, namespaces):
        self.namespaces = namespaces

identifiers = SBOLIdentifiers()
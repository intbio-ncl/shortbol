import rdflib
import os
from .logic import And
from .error import ExtensionError
from rdfscript.core import Uri, Value

sbolns = Uri('http://sbols.org/v2#')
# other special URIs in the context of SBOL compliant URIs
rdf_type = Uri(rdflib.RDF.type)

combinatorial_derivation_type =  Uri(sbolns.uri + "CombinatorialDerivation")
template_type =                  Uri(sbolns.uri + "template")
variable_component_predicate =   Uri(sbolns.uri + "variableComponent")
variable_predicate =             Uri(sbolns.uri + "variable")
variant_predicate =              Uri(sbolns.uri + "variant")
variant_collection_predicate =   Uri(sbolns.uri + "variantCollection")
collection_member_predicate =    Uri(sbolns.uri + "member")
component_predicate =            Uri(sbolns.uri + "component")
sbol_definition =                Uri(sbolns.uri + "definition")
component_access_predicate =     Uri(sbolns.uri + "access")
component_access_object_public = Uri(sbolns.uri + "public")
component_type =                 Uri(sbolns.uri + "Component")
sequence_constraint_predicate =  Uri(sbolns.uri + "sequenceConstraint")
sequence_constraint_subject =    Uri(sbolns.uri + "subject")  
sequence_constraint_object =     Uri(sbolns.uri + "object")
sequence_annotation_predicate =  Uri(sbolns.uri + "sequenceAnnotation")
location_predicate =             Uri(sbolns.uri + "location")

class CombinatorialDerivation:
    def __init__(self,cd_name):
        self.cd_name = cd_name
        pass

    def run(self, triplepack):
        extension_param_type = list(get_possible_SBOL_types(triplepack,self.cd_name))
        if len(extension_param_type) == 0 or len(extension_param_type) > 1:
            raise ValueError("Template provided for Extension either does not exist or two templates of the same name are present.")
        if extension_param_type[0] != combinatorial_derivation_type:
            raise ValueError("Template provided is not a Combinatorial Derivation template.")
        template = triplepack.search((self.cd_name,template_type,None))[0]
        template = triplepack.search((template[2],None,None))
        

        variable_component_names = triplepack.search((self.cd_name,variable_component_predicate,None))
        for variable_component_name in variable_component_names:
            variable = triplepack.search((variable_component_name[2],variable_predicate,None))[0]
            variants = get_variants(variable_component_name[2], triplepack)
            
            if variable[2] not in [n[2] for n in template]:
                raise ValueError(f'The variable object {variable[2]} is not a sub-component of the Template {template[0][0]}.')
            
            for variant in variants:
                new_template_name = Uri(template[0][0].uri + "_" + variable_component_name[2].uri.split("/")[-1] + "_" + variant[2].uri.split("/")[-1])
                for s,p,o in template:
                    # When the triple pertains to the variable component.
                    if variable[2] == o:
                        # Variant is a CD need Component
                        component_name = generate_name(variant,o)
                        component = generate_component(variant[2],component_name)
                        for c_t in component:
                            triplepack.add((c_t[0],c_t[1],c_t[2]))
                        o = component_name
                    # A component that is NOT the variable component.
                    elif p == component_predicate:
                        component_name = generate_name(variant,o)
                        definition = triplepack.search((o, sbol_definition, None))
                        component = generate_component(definition[0][2], component_name)
                        for c_t in component:
                            triplepack.add((c_t[0],c_t[1],c_t[2]))
                        o = component_name
                    # A Sequence Constraint.
                    elif p == sequence_constraint_predicate:
                        # A constraint requires:
                        # A new name
                        constraint_name = generate_name(variant,o)
                        # The previous constraint being copied triples.
                        constraint_triples = triplepack.search((o,None,None))
                        # The New Subject and Object triples.
                        # Note there is a de-link here where we are assuming that the name of the subject and object.
                        subject = triplepack.search((o,sequence_constraint_subject,None))
                        object = triplepack.search((o,sequence_constraint_object,None))
                        subject_name = generate_name(variant,subject[0][2])
                        object_name = generate_name(variant,object[0][2])

                        constraint = generate_constraint(constraint_triples,constraint_name,subject_name,object_name)
                        for c_t in constraint:
                            triplepack.add((c_t[0],c_t[1],c_t[2]))
                        o = constraint_name

                    # A Sequence Annotation.
                    elif p == sequence_annotation_predicate:
                        # A annotation needs:
                        component = triplepack.search((o,component_predicate,None))
                        component_name = generate_name(variant,component[0][2])
                    
                        # A new location
                        location = triplepack.search((o,location_predicate,None))
                        location_name = generate_name(variant,location[0][2])
                        location_triples = triplepack.search((location[0][2],None,None))
                        location = generate_location(location_triples,location_name)
                        for c_t in location:
                            triplepack.add((c_t[0],c_t[1],c_t[2]))

                        # A new SequenceAnnoation
                        annotation_name = generate_name(variant,o)
                        annotation_triples = triplepack.search((o,None,None))
                        annotation = generate_annotation(annotation_triples,annotation_name,location_name,component_name)
                        for c_t in annotation:
                            triplepack.add((c_t[0],c_t[1],c_t[2]))
                    
                        o = annotation_name
                    # Any other triples that can just be copied directly (names, descriptions etc)
                    else:
                        pass

                    triplepack.add((new_template_name, p, o))
            for n in triplepack.search((variable_component_name[2],None,None)):
                triplepack.triples.remove(n)
        for triple in triplepack.search((self.cd_name,None,None)):
            triplepack.triples.remove(triple)
        return triplepack


def get_variants(variable_component_name, triplepack):
    variants = []
    variants = variants + triplepack.search((variable_component_name,variant_predicate,None))

    variant_collection_names = triplepack.search((variable_component_name,variant_collection_predicate,None))
    # For each Collection Template
    for variant_collection_name in variant_collection_names:
        # For each member of Collection
        variants = variants + triplepack.search((variant_collection_name[2],collection_member_predicate,None))
    return variants

def get_possible_SBOL_types(triplepack, uri):
    '''
    Return the possible SBOL object types based on the RDF.type
    property attached to uri.

    '''
    return {o for (s, p, o) in triplepack.search((uri, rdf_type, None))}

def generate_name(variant,name):
    '''
    Essentially prefixes the oldname with the current variant name
    '''
    return Uri(variant[2].uri  + "_" + name.uri.split("/")[-1])
    
def generate_component(parent,component_name):
    new_component = []
    definition = (Uri(component_name), sbol_definition, parent)
    access = (Uri(component_name), component_access_predicate, component_access_object_public )
    type = (Uri(component_name), rdf_type, component_type)
    new_component.append(definition)
    new_component.append(access)
    new_component.append(type)
    return new_component
    
def generate_constraint(constraint_triples,constraint_name,subject_name,object_name):
    new_constraint = []
    for s,p,o in constraint_triples:
        # Subject - Need new component Name
        if p == sequence_constraint_subject:
            o = subject_name
        elif p == sequence_constraint_object:
            o = object_name
        new_constraint.append((Uri(constraint_name),p,o))
        
    return new_constraint
    
def generate_location(location_triples,location_name):
    new_location = []
    for s,p,o in location_triples:
        new_location.append((Uri(location_name),p,o))
    return new_location

def generate_annotation(annoation_triples,annotation_name,location_name,component_name):
    new_annotation = []
    for s,p,o in annoation_triples:
        if p == location_predicate:
            o = location_name
        elif p == component_predicate:
            o = component_name
        new_annotation.append((Uri(annotation_name),p,o))
    return new_annotation
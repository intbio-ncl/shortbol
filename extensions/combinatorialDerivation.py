import rdflib
import os
from .logic import And
from .error import ExtensionError
from rdfscript.core import Uri, Value
from sbol_rdf_identifiers import identifiers

class CombinatorialDerivation:
    def __init__(self,cd_name):
        self.cd_name = cd_name

    def run(self, triplepack, env):
        if env.version == "sbol_2":
            return self.run_sbol_2(triplepack,env)

        if env.version == "sbol_3":
            print("Running dis...")
            return self.run_sbol_3(triplepack,env)
            

    def run_sbol_2(self,triplepack,env):
        if not is_param_valid(triplepack, self.cd_name):
            raise ValueError("Extension Parameter is Invalid")

        template = get_template(triplepack,self.cd_name)

        variable_component_names = triplepack.search((self.cd_name,identifiers.predicates.variable_component,None))
        for variable_component_name in variable_component_names:
            variable = triplepack.search((variable_component_name[2],identifiers.predicates.variable,None))[0]
            variants = get_variants(variable_component_name[2], triplepack)
            if variable[2] not in [n[2] for n in template]:
                raise ValueError(f'The variable object {variable[2]} is not a sub-component of the Template {template[0][0]}.')
            
            for variant in variants:
                new_template_name = Uri(template[0][0].uri + "_" + variable_component_name[2].split()[-1] + "_" + variant[2].split()[-1])
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
                    elif p == identifiers.predicates.component:
                        component_name = generate_name(variant,o)
                        definition = triplepack.search((o, identifiers.predicates.definition, None))
                        component = generate_component(definition[0][2], component_name)
                        for c_t in component:
                            triplepack.add((c_t[0],c_t[1],c_t[2]))
                        o = component_name
                    # A Sequence Constraint.
                    elif p == identifiers.predicates.sequence_constraint:
                        # A constraint requires:
                        # A new name
                        constraint_name = generate_name(variant,o)
                        # The previous constraint being copied triples.
                        constraint_triples = triplepack.search((o,None,None))
                        # The New Subject and Object triples.
                        # Note there is a de-link here where we are assuming that the name of the subject and object.
                        subject = triplepack.search((o,identifiers.predicates.subject,None))
                        object = triplepack.search((o,identifiers.predicates.object,None))
                        subject_name = generate_name(variant,subject[0][2])
                        object_name = generate_name(variant,object[0][2])

                        constraint = generate_constraint(constraint_triples,constraint_name,subject_name,object_name)
                        for c_t in constraint:
                            triplepack.add((c_t[0],c_t[1],c_t[2]))
                        o = constraint_name

                    # A Sequence Annotation.
                    elif p == identifiers.predicates.sequence_annotation:
                        # A annotation needs:
                        component = triplepack.search((o,identifiers.predicates.component,None))
                        component_name = generate_name(variant,component[0][2])
                    
                        # A new location
                        location = triplepack.search((o,identifiers.predicates.location,None))
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


    def run_sbol_3(self,triplepack,env):
        identifiers.swap_version("sbol_3")
        if not is_param_valid(triplepack, self.cd_name):
            raise ValueError("Extension Parameter is Invalid")

        template = get_template(triplepack,self.cd_name)
        variable_component_names = triplepack.search((self.cd_name,identifiers.predicates.has_variable_component,None))
        
        for variable_component_name in variable_component_names:
            variable = triplepack.search((variable_component_name[2],identifiers.predicates.variable,None))[0]
            variants = get_variants(variable_component_name[2], triplepack)

            if variable[2] not in [n[2] for n in template]:
                raise ValueError(f'The variable object {variable[2]} is not a sub-component of the Template {template[0][0]}.')
            
            for variant in variants:
                new_template_name = Uri(template[0][0].uri + "_" + variable_component_name[2].split()[-1] + "_" + variant[2].split()[-1])
                for s,p,o in template:
                    # When the triple pertains to the variable component.
                    if variable[2] == o:
                        # Variant is a CD need Component
                        component_name = generate_name(variant,o)
                        component = generate_sub_component(variant[2],component_name)
                        for c_t in component:
                            triplepack.add((c_t[0],c_t[1],c_t[2]))
                        o = component_name

                    # A component that is NOT the variable component.
                    elif p == identifiers.predicates.has_feature:
                        component_name = generate_name(variant,o)
                        definition = triplepack.search((o, identifiers.predicates.instance_of, None))[0]
                        component = generate_sub_component(definition[2], component_name)
                        locations = triplepack.search((o,identifiers.predicates.has_location,None))
                        if len(locations) != 0:
                            for location in locations:
                                component = component + generate_location_sbol_3(location,definition,triplepack)
                        for c_t in component:
                            triplepack.add((c_t[0],c_t[1],c_t[2]))
                        o = component_name
                        
                    # A Sequence Constraint.
                    elif p == identifiers.predicates.has_constraint:
                        # A constraint requires:
                        # A new name
                        constraint_name = generate_name(variant,o)
                        # The previous constraint being copied triples.
                        constraint_triples = triplepack.search((o,None,None))
                        # The New Subject and Object triples.
                        # Note there is a de-link here where we are assuming that the name of the subject and object.
                        subject = triplepack.search((o,identifiers.predicates.subject,None))
                        object = triplepack.search((o,identifiers.predicates.object,None))
                        subject_name = generate_name(variant,subject[0][2])
                        object_name = generate_name(variant,object[0][2])

                        constraint = generate_constraint(constraint_triples,constraint_name,subject_name,object_name)
                        for c_t in constraint:
                            triplepack.add((c_t[0],c_t[1],c_t[2]))
                        o = constraint_name
                    # Any other triples that can just be copied directly (names, descriptions etc)
                    else:
                        pass

                    triplepack.add((new_template_name, p, o))

            for n in triplepack.search((variable_component_name[2],None,None)):               
                triplepack.triples.remove(n)
        for triple in triplepack.search((self.cd_name,None,None)):
            triplepack.triples.remove(triple)
        return triplepack


def get_template(triplepack, cd_name):
    template = triplepack.search((cd_name,identifiers.predicates.template,None))[0]
    template = triplepack.search((template[2],None,None))
    return template

def is_param_valid(triplepack,cd_name):
    extension_param_type = list(get_possible_SBOL_types(triplepack, cd_name))
    if len(extension_param_type) == 0 or len(extension_param_type) > 1:
        raise ValueError("Template provided for Extension either does not exist or two templates of the same name are present.")
    if extension_param_type[0] != identifiers.objects.combinatorial_derivation:
        raise ValueError("Template provided is not a Combinatorial Derivation template.")
    return True

def get_variants(variable_component_name, triplepack):
    variants = []
    variants = variants + triplepack.search((variable_component_name,identifiers.predicates.variant,None))

    variant_collection_names = triplepack.search((variable_component_name,identifiers.predicates.variant_collection,None))
    # For each Collection Template
    for variant_collection_name in variant_collection_names:
        # For each member of Collection
        variants = variants + triplepack.search((variant_collection_name[2],identifiers.predicates.member,None))
    return variants

def get_possible_SBOL_types(triplepack, uri):
    '''
    Return the possible SBOL object types based on the RDF.type
    property attached to uri.

    '''
    return {o for (s, p, o) in triplepack.search((uri, identifiers.predicates.rdf_type, None))}

def generate_name(variant,name):
    '''
    Essentially prefixes the oldname with the current variant name
    '''
    return Uri(variant[2].uri  + "_" + name.split()[-1])
    
def generate_component(parent,component_name):
    new_component = []
    definition = (Uri(component_name), identifiers.predicates.definition, parent)
    access = (Uri(component_name), identifiers.predicates.access, identifiers.predicates.public )
    type = (Uri(component_name), identifiers.predicates.rdf_type, identifiers.objects.component)
    new_component.append(definition)
    new_component.append(access)
    new_component.append(type)
    return new_component

def generate_sub_component(parent,component_name):
    new_component = []
    definition = (Uri(component_name), identifiers.predicates.instance_of, parent)
    type = (Uri(component_name), identifiers.predicates.rdf_type, identifiers.objects.sub_component)
    new_component.append(definition)
    new_component.append(type)
    return new_component
    

def generate_constraint(constraint_triples,constraint_name,subject_name,object_name):
    new_constraint = []
    for s,p,o in constraint_triples:
        # Subject - Need new component Name
        if p == identifiers.predicates.subject:
            o = subject_name
        elif p == identifiers.predicates.object:
            o = object_name
        new_constraint.append((Uri(constraint_name),p,o))
        
    return new_constraint
    
def generate_location(location_triples,location_name):
    new_location = []
    for s,p,o in location_triples:
        new_location.append((Uri(location_name),p,o))
    return new_location

def generate_location_sbol_3(location,definition,triplepack):
    new_location = []
    location_name = Uri(definition[2].uri + "_loc")
    location_triples = triplepack.search((location[2],None,None))
    sequence = triplepack.search((definition[2],identifiers.predicates.has_sequence,None))[0]
    if len(sequence) == 0:
        return []    
    new_location.append((location_name,identifiers.predicates.has_sequence,sequence[2]))

    for s,p,o in location_triples:
        if p == identifiers.predicates.rdf_type:
            new_location.append((location_name,p,o))
        elif p == identifiers.predicates.has_sequence:
            # We want to remove the current sequence.
            pass
        else:
            new_location.append((location_name,p,o))
    return new_location

def generate_annotation(annoation_triples,annotation_name,location_name,component_name):
    new_annotation = []
    for s,p,o in annoation_triples:
        if p == identifiers.predicates.location:
            o = location_name
        elif p == identifiers.predicates.component:
            o = component_name
        new_annotation.append((Uri(annotation_name),p,o))
    return new_annotation
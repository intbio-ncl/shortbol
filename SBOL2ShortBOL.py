
import os
import re
import json
import sys
import rdflib
import rdflib.compare
import argparse
import validate_sbol
from run import produce_tables

sbolns = rdflib.URIRef('http://sbols.org/v2#')
top_levels = {rdflib.URIRef(sbolns + name) for name in
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

ownership_predicates = {rdflib.URIRef(sbolns + predicate) for predicate in
                        ['module',
                         'mapsTo',
                         'interaction',
                         'participation',
                         'functionalComponent',
                         'sequenceConstraint',
                         'location',
                         'sequenceAnnotation',
                         'variableComponent']}                    


required_properties = {rdflib.URIRef(sbolns + property) for property in
                        ['version',
                         'persistentIdentity',
                         'displayId']}
                         
sbh_namespace = rdflib.URIRef("http://wiki.synbiohub.org/wiki/Terms/synbiohub#")
igem_namespace = rdflib.URIRef("http://wiki.synbiohub.org/wiki/Terms/igem#")
dc_terms_namespace = rdflib.URIRef("http://purl.org/dc/terms/")
provo_namespace = rdflib.URIRef("http://www.w3.org/ns/prov#")
prune_namespaces = [sbh_namespace,igem_namespace]

rdf_type = rdflib.URIRef(rdflib.RDF.type)
component = rdflib.URIRef(sbolns+ 'component')
cd = rdflib.URIRef(sbolns + 'ComponentDefinition')
sa = rdflib.URIRef(sbolns + 'SequenceAnnotation')

dc_title = rdflib.URIRef("http://purl.org/dc/terms/title")




def produce_shortbol(sbol_xml_fn, shortbol_libary, output_fn = None, no_validation = False, prune = False, prune_list = None):
    # Perform full file validation before producing ShortBOL.
    if not no_validation and not general_validation(sbol_xml_fn):
         print("Warn:: Can't validate input.")
    g=rdflib.Graph()
    g.load(sbol_xml_fn)

    # Manipulate the triplepack to move from a graph structure to 
    # an easier to use tree form.
    heirachy_tree = {}
    tree_roots = find_graph_roots(g)
    # We can (and likely will with larger designs) have 
    # multiple roots which means multiple trees,
    # So the first level of the dict is multiple roots.
    for root in tree_roots:
        heirachy_tree[str(root[0])] = get_tree(g,root[0],prune = prune,prune_list = prune_list)

    # Now have a structure that is easier to use.
    # Create the actual ShortBOL from this.
    shortbol_code = convert(heirachy_tree,shortbol_libary)

    if output_fn is None:
        print(shortbol_code)
        return shortbol_code
    else:
        if os.path.isfile(output_fn):
            os.remove(output_fn)
        f = open(output_fn,"a")
        f.write(shortbol_code)
        f.close()
        return output_fn
    return

def find_graph_roots(graph):
    '''
    Find root nodes of graph.
    root nodes can be defined by 
        TopLevel entities - The Object is contained within the toplevels set.
        No Parents - When the subject is not a object of another triple.
                     Unless the predicate is NOT in the ownership_predicates set. 
    '''
    roots = set()
    for s,p,o in graph:
        if o in top_levels:
            if get_possible_parents(s,graph):
                raise ValueError("TopLevel with parent.")
            roots.add((s,p,o))
    return roots

# Problem the get children is always for the master parent.
def get_tree(graph,root,done = None, prune = False, prune_list = None):
    if done is None:
        done = set()
    if root in done:
        return
    done.add(root)
    tree = []
    children = get_children(root,graph)
    # Just saying get all related triples that aren't children
    # Also Take a reference to child as property.
    properties = set([prop for prop in search((root,None,None),graph) ])
    for child in children:
        t = get_tree(graph, child[2], done, prune = prune, prune_list = prune_list)
        if t:
            ch = {str(child[2]) : t}
            tree.append(ch)

    for prop in properties:
        # Flag that removes any triples that are in namespace list.
        if prune_list is not None and any(ns in prop[1] for ns in prune_list):
            continue
        if prune and any(ns in prop[1] for ns in prune_namespaces):
            continue
        tree.append((prop))
    return tree


def convert(heirachy_tree,shortbol_libary):
    symbol_table,template_table,prefixes = produce_tables(lib_paths = shortbol_libary)
    template_table = cast_to_rdflib(template_table)
    symbol_table = cast_to_rdflib(symbol_table)
    prefixes = add_unknown_prefixes(heirachy_tree,prefixes,symbol_table)
    #@@TMPREMOVAL@@
    prefixes = {"prefixes":[],"unknown_prefixes":[]}
    ordered_parameter_lists = get_parameter_lists(template_table,shortbol_libary)

    shortbol_code = ""

    for name,triples in heirachy_tree.items():
        shortbol_code = shortbol_code + handle_template(name,triples,template_table,symbol_table,ordered_parameter_lists,prefixes)
    for unknown_prefix_name,unknown_prefix in prefixes["unknown_prefixes"]:
        if unknown_prefix_name in shortbol_code:
            shortbol_code = create_prefix_code(unknown_prefix_name,unknown_prefix) + shortbol_code
             

    return shortbol_code


def handle_template(name,triples,template_table,symbol_table,ordered_parameter_lists,prefixes):
    shortbol_code = ""
    template_name = get_name(name)
    properties = [triple for triple in triples if isinstance(triple,tuple)]
    children = [triple for triple in triples if isinstance(triple,dict)]
    template_type = get_possible_SBOL_types(properties,name)
    
    if len(template_type) == 1:
        template_type = split(list(template_type)[0])[-1]
    elif len(template_type) == 0:
        raise ValueError("Unable to find type for: " + str(name))
    elif len(template_type) > 1:
        raise ValueError("Found more than one type for: " + str(name))
    
    # We have decided that we will convert to abstract layer 1 only. 
    specialised_templates = get_specialised_templates(template_type,template_table,symbol_table)

    # Try create a specialised template
    for k in sorted(specialised_templates, key=lambda k: len(specialised_templates[k]), reverse=True):
        def inline_matcher(item):
            for s_s,s_p,s_o in item:
                if (s_p,s_o) not in [(p,o) for s,p,o in properties]:
                    return False
            return True

        if inline_matcher(specialised_templates[k]):
            temp_properties = []
            # Specialised template is created, remove those triples.
            for s,p,o in properties:
                if (p,o) not in [(s_p,s_o) for s_s,s_p,s_o in specialised_templates[k]]:
                    temp_properties.append((s,p,o))
            properties = temp_properties
            template_type = split(k)[-1]
            break
    
    # Need define parameters (With positions) and expansion properties (with prop name)
    # Required parameters will always be present in the template table (Need to find position tho)
    un_ordered_parameters = []
    ordered_parameters = []
    expansion_properties = []
    for s,p,o in properties:
        if p in required_properties:
            # Properties that we dont need to handle.
            continue
        if p == rdf_type:
            # Handled this already
            continue
        if p in [p for (s,p,o) in template_table[sbolns + template_type]]:                
            # The property is a ShortBOL parameter
            # Note at this point the parameters are potentially in the incorrect order.
            obj = handle_object(o,symbol_table)
            un_ordered_parameters.append((p,obj))
        else:
            # The property must be an expansion property
            obj = handle_object(o,symbol_table)
            # Certain properties need there prefixes conserved
            prefix = lookup_prefix_name(o,prefixes)
            if prefix is not None:
                obj = prefix + "." + obj

            # Another quirk of SBOL, one of the only cases when SBOL aliases, (sbol name == "dcterms title")
            if p == dc_title:
                p = "name"
            expansion_properties.append((get_name(p),obj))

    # Sort the parameters list so that they are in the correct position.
    for ordered_p in ordered_parameter_lists[template_type]:
        for p,o in un_ordered_parameters:
            if ordered_p == p:
                ordered_parameters.append(o)
                
    #Handle children and linkage.
    for child in children: 
        name = list(child.keys())[0]
        triples = [j for i in list(child.values()) for j in i]
        shortbol_code = shortbol_code + handle_template(name,triples,template_table,symbol_table,ordered_parameter_lists,prefixes)

    shortbol_code = shortbol_code + create_instance(template_name, template_type, ordered_parameters, expansion_properties)    
    return shortbol_code

def handle_object(o,symbol_table):
    '''
    The properties object can be multiple things:
    A literal:
        A string
        A number
    A URI
        A Reference to another template
        A Reference to an external resource.
    '''
    if isinstance(o,rdflib.Literal):
        if o.isdigit():
            obj = o
        else:
            obj = f'"{o}"'
    elif isinstance(o,rdflib.URIRef):
        # Is the URI a reference to another template or external URI
        if o in symbol_table.values():
            for k,v in symbol_table.items():
                if v == o:
                    obj = k
                    break
        else:
            # A reference to an external URI is different, we need to preserve the Prefix.
            obj = o
        obj = get_name(obj)
    else:
        raise TypeError(f'{o} is a type that ShortBOL does not support.') 

    return obj

def get_specialised_templates(base_name,template_table,symbol_table):
    '''
    a specialised tmpl is when the object of the type triple is equal to the base_name
    Then we need what properties make this a specialised template.
    Then we take the properties are required values of these properties.
    However we only want layer 1 specialised templates.
    '''
    temp_table = []
    children = {}
    for template_name, triples in template_table.items():
        template_type = [(s,p,o) for s,p,o in triples if p == rdf_type]
        # It is attempt to only take layer one templates, we are assuming either the template will reference more than one other template OR the self will have a longer name.
        if len(template_type) > 1 or len([(s,p,o) for s,p,o in template_type if s != rdflib.URIRef("self")]) > 0 :
            continue
        elif len(template_type) == 1:
            template_type = template_type[0][2]
        else:
            # There are some very base templates which are typeless such as addProperty so just skip.
            # (The user would never instantiate these templates)
            continue
        if split(template_type)[-1] == base_name:
            if split(template_name)[-1] == base_name:
                continue
            temp_table.append(template_type)
            children[template_name] = []
            for s,p,o in triples:
                if o in symbol_table.values():
                    children[template_name].append((s,p,o))
    return children

def get_name(item):
    split_item = split(item)
    if len(split_item[-1]) == 1 and split_item[-1].isdigit():
        return split_item[-2]
    else:
        return split_item[-1]

def split(uri):
    return re.split('#|\/|:', uri)

def get_prefix(uri):
    '''
    Simply removes the last part of a URI and returns the Prefix
    '''

    if not isinstance(uri,rdflib.URIRef):
        raise ValueError(f'{uri} is not a URI.')
    split_item = split(uri)
    if len(split_item) > 2 and len(split_item[-1]) == 1 and split_item[-1].isdigit()  :
        name = split_item[-2] + "/" + split_item[-1]
    else:
        name = split_item[-1]

    # Cant just remove the name string because the prefix MIGHT have the name in the prefix.
    prefix = rdflib.URIRef(uri[0:len(uri) - len(name)])
    return prefix


def lookup_prefix_name(object,prefixes):
    '''
    Looks up the prefix in the prefixes struct to find the substitution name.
    '''
    if not isinstance(object,rdflib.URIRef):
        return None
    for prefix in prefixes["prefixes"]:
        if get_prefix(object) == prefix[1]:
            return prefix[0]
    for prefix in prefixes["unknown_prefixes"]:
        if get_prefix(object) == prefix[1]:
            return prefix[0]
            

def add_unknown_prefixes(heirachy_tree,prefixes,symbol_table):
    # For the case when a URI has a Prefix that isn't defined in the ShortBOL libaries
    new_prefixes = []
    symbol_uris = [v for k,v in symbol_table.items()]
        
    def inner_prefix(uri):
        if isinstance(uri,rdflib.URIRef):
            # If the URI isnt defined as a prefix but has a name in the symbols table don't need to add prefix for this.
            if uri in symbol_uris:
                return
            prefix = get_prefix(uri)
            if prefix in [prefix[1] for prefix in new_prefixes]:
                return
            if not prefix in [prefix[1] for prefix in prefixes]: 
                # Generate a unique name for this prefix based on its uri.
                parts = split(prefix)
                name = parts[3].split(".")[0] + "_" + parts[-2]
                new_prefixes.append((name,prefix))
            
    def add_unknown_prefixes_inner(item,f=None,indent=""):
        for top_level,branches in item.items():
            # Each key is a str
            inner_prefix(top_level)
            # Branches always come as a list
            for branch in branches:
            # A branch can be:
                # A tuple - When its a property
                if isinstance(branch,tuple):
                    for uri in branch:
                        inner_prefix(uri)
                # A list - When its a child
                elif isinstance(branch,dict):
                    add_unknown_prefixes_inner(branch)
                else:
                    raise ValueError(f"The value is not a dict or tuple: {str(branch)}")
    add_unknown_prefixes_inner(heirachy_tree)
    
    prefixes = {"prefixes":prefixes,"unknown_prefixes":new_prefixes}
    return prefixes

def cast_shortbol_uri(uri):
    '''
    Because ShortBOL uri's when cast to string
    contain chevrons at each side comparing to
    RDFlib objects are not compatible 

    '''
    return rdflib.URIRef(str(uri).replace("<","").replace(">",""))

def cast_to_rdflib(item):
    new_struct = dict()
    for key,value in item.items():
        if isinstance(value,(list,tuple,set)):
            new_triplepack = list()
            for triple in value:
                new_triplepack.append((cast_shortbol_uri(triple[0]), cast_shortbol_uri(triple[1]), cast_shortbol_uri(triple[2])))
            new_struct[cast_shortbol_uri(key)] = new_triplepack
        else:
            new_struct[cast_shortbol_uri(key)] = cast_shortbol_uri(value)
    return new_struct



def get_possible_parents(child,triplepack):
    possible_parents = set()
    for predicate in ownership_predicates:
        possible_parents |= {s for (s, p, o) in search((None, predicate, child),triplepack)}
    return possible_parents


def get_children(parent,triplepack):
    possible_parents = set()
    for predicate in ownership_predicates:
        possible_parents |= {(s,p,o) for (s, p, o) in search((parent, predicate, None),triplepack)}
    # now for the components
    possible_parents |= {(s,p,o) for (s, p, o)
                         in search((parent, component, None),triplepack)
                         if cd in get_possible_SBOL_types(triplepack, s)
                         and sa not in get_possible_SBOL_types(triplepack, s)}

    return possible_parents

def get_possible_SBOL_types(triplepack, uri):
    '''
    Return the possible SBOL object types based on the RDF.type
    property attached to uri.

    '''
    if not isinstance(uri,rdflib.URIRef):
        uri = rdflib.URIRef(uri)

    return {o for (s, p, o) in search((uri, rdf_type, None),triplepack)}

def search(pattern,triples):
    (s, p, o) = pattern

    def matcher(triple):
        (x, y, z) = triple
        return ((x == s or not s) and
                (y == p or not p) and
                (z == o or not o))
    
    return [t for t in triples if matcher(t)]

def general_validation(sbol_xml_fn):
    with open(sbol_xml_fn,"r") as sbol:
        response = validate_sbol.validate_sbol(sbol.read())
        try:
            if response['valid']:
                return True
            elif response is None:
                return False
            else:
                for e in response['errors']:
                    print(e)
                raise ValueError("Unable to produce ShortBOL because provided SBOL is invalid.")
        except TypeError:
            return False


def create_instance(name, template_type, parameters = None, expansions = None):
    '''
    Creates the instance of a Shortbol object, ie actually creates the text.
    '''
    template = f'\n{name} is a {template_type}'
    template = f'{template}('

    if parameters is not None and len(parameters) > 0:
        for index, parameter in enumerate(parameters):
            if index + 1 != len(parameters):
                template = template + str(parameter) + ", "
            else:
                template = template + str(parameter)
    template = f'{template})'

    if expansions is not None and len(expansions) != 0:
        expansions = sorted(expansions, key=lambda tup: tup[0])
        template = f'{template}\n(\n'
        for expansion in expansions:
            template = f'{template}     {expansion[0]} = {expansion[1]}\n'
        template = f'{template})\n'
    return template

def create_prefix_code(name,prefix):
    return f'\n@prefix {name} = <{prefix}>'

def get_parameter_lists(template_table,shortbol_libary):
    '''
    This is a hack, because it is not possible to find the order of parameters from the template table
    For example Range(start,end,direction)
    We don't know what the correct order is from the template table because the assumption can't 
    be made that the template table properties are always in the same order as the parameter list.
    Therefore, It is needed to articifially find these orders from the raw template files.
    Said assumption could be made IF the property assignments where in the order or the parameter list for example:
    Range(start,end,direction)
    (
        sbol.start = start
        sbol.end = end
        sbol.direction = diretion
    )
    However if this assumption would be taken then this rule would always have to be enforced which is arguably more
    hacky than this hack.
    This hack instead reads the libary and uses regex to make ordered lists corresponding to param list
    '''
    sbol_sbh_lib = os.path.join(shortbol_libary,"sbol_2")
    parameter_list = {}
    template_re = re.compile(".+[(].*[)]")
    single_line_template_re = re.compile(".+[(].*[)][(].*[)]")
    for filename in os.listdir(sbol_sbh_lib):
        if os.path.isfile(os.path.join(sbol_sbh_lib,filename)): 
            template = open(os.path.join(sbol_sbh_lib, filename), "r")
            lines = template.readlines()
            template.close()
            lines = [line.replace(" ","").replace("\n","").replace("\t","").lstrip().rstrip() 
                     for line in lines]

            for index, line in enumerate(lines):
                if index + 1 > len(lines) or line is None or line == "" or "isa" in line:
                    continue
                
                line_re = template_re.match(line)
                single_line_re = single_line_template_re.match(line)

                template_type = None
                if index + 1 < len(lines) and line_re is not None and lines[index + 1] == "(":
                    template_type = line.split("(")[0]
                    curr_line = line
                # Little awkward case where the expansion is on the same line as the 
                # Template type for examople:
                #ModuleDefinition() (TopLevel(ModuleDefinition))
                elif single_line_re is not None:
                    template_type = line.split("(")[0]
                    curr_line =  line.split(")")[0]
                if template_type is not None:
                    parameters = get_parameters(curr_line,index)
                    # The parameters don't always link to the property names,
                    # Query the Template table and swap o for p (property is always the correct name) 
                    for s,p,o in template_table[cast_shortbol_uri(sbolns + template_type)]:
                        for index,param in enumerate(parameters):
                            if cast_shortbol_uri(param) == o:
                                parameters[index] = p

                    if len(parameters) == 1 and parameters[0] == "":
                        parameters = []
                    parameter_list[template_type] = parameters
    return parameter_list

def get_parameters(line,line_no):
    parameters = []
    try:
        parameters = line.split("(")[1]
        parameters = parameters.replace("(","").replace(")","").replace(" ","").split(",")
    except IndexError:
        raise NameError(f"Error Parameters on line: {line_no - 2} is malformed.")
    return parameters


def sbol_2_shortbol_args():
    parser = argparse.ArgumentParser(description="Tool to generate shortbol code from SBOL RDF/XML")
    parser.add_argument('filename', default=None, nargs='?',
                        help="RDF/XML to produce ShortBOL")
    parser.add_argument('-o ','--output', default=None, 
                        help="Filename to write ShortBOL to. If no arg provided will print to stdout.")
    parser.add_argument('-p ','--path', default=os.path.join("templates"), 
                        help="specify path to shortbol libary.")
    parser.add_argument('-nv', '--no_validation', help="Stops the Input from being sent via HTTP to online validator.", default=None, action='store_true')
    parser.add_argument('-prune', '--prune', help=f"This flag will remove the properties from {str([str(namespace) for namespace in prune_namespaces])} Namespaces.", default=False, action='store_true')
    return  parser.parse_args()


if __name__ == "__main__":
    args = sbol_2_shortbol_args()
    produce_shortbol(args.filename, args.path, args.output, args.no_validation, args.prune)








import rdflib
import os
from .logic import And
from .error import ExtensionError
from rdfscript.core import Uri, Value

sbolns = Uri('http://sbols.org/v2#')

# the names of 'Top Level' objects, those whose serialisations are not
# nested inside the serialisations of other objects
toplevels = {Uri(sbolns.uri + name) for name in
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


# the predicates that indicate that a subject is a parent of an object
# this does not include 'component' which does not necessarily
# indicate such a relationship
ownership_predicates = {Uri(sbolns.uri + predicate) for predicate in
                        ['module',
                         'mapsTo',
                         'interaction',
                         'participation',
                         'functionalComponent',
                         'sequenceConstraint',
                         'location',
                         'sequenceAnnotation',
                         'variableComponent']}




# other special URIs in the context of SBOL compliant URIs
persistentIdentity = Uri(sbolns.uri + 'persistentIdentity')
displayId = Uri(sbolns.uri + 'displayId')
version = Uri(sbolns.uri + 'version')
rdf_type = Uri(rdflib.RDF.type)


class SbolIdentity:
    '''
    Extension which checks all SBOL objects contained in a triplepack
    have SBOL compliant URIs, and if not, attempts to modify the
    triples such that they are.

    Creates a single SBOLCompliant extension for each named SBOL
    object (subject) in the triplepack and 'ANDs' them together. The
    extension returns successful if all the SBOL objects in the
    triplepack have SBOL compliant URIs, or can be modified to have
    them. Otherwise fails and raises Exception.

    Note: the And extension is short-circuiting TODO: decide if this
    is the desired behaviour for SBOLIdentity
    '''

    def __init__(self):
        pass

    def run(self, triplepack):
        subjects = list(triplepack.subjects)
        identifiers = get_identifier_uris(triplepack._paths)

        for i in range(len(subjects)):
            SBOLCompliant(subjects[i], identifiers).run(triplepack, subjects)

        return triplepack


class SBOLCompliant:
    '''
    Extension to check a single subject, naming an SBOL object, has an
    SBOL compliant URI, and if not, attempts to modify triplepack such
    that they are.
    '''
    def __init__(self, for_subject, identifiers):
        self.subject = for_subject
        self.identifiers = identifiers

    def run(self, triplepack, subjects):
        

        if not is_valid_parameters(self.identifiers, triplepack,subjects):
            raise SBOLComplianceError(f"Invalid Parameter type for {subjects}")

        parent = get_SBOL_parent(triplepack, self.subject)
        # Everything has a display id
        if not triplepack.search((self.subject, displayId, None)):
            if parent is not None:
                new_displayId = self.subject.split()[-1]
                #for part in parent.split():
                    #new_displayId = new_displayId.replace(part,"")
            else:
                new_displayId = self.subject.split()[-1]
        
            triplepack.add((self.subject, displayId, Value(new_displayId)))
        # Everything has a Version
        if get_SBOL_version(triplepack, self.subject) is None:
            #Set default version of 1.
            triplepack.add((self.subject, version, Value("1")))



        if parent is not None:
            # its a child
            if not triplepack.has(parent, persistentIdentity):
                SBOLCompliant(parent,self.identifiers).run(triplepack, subjects)

            # parent uri might have changed!!!
            parent = get_SBOL_parent(triplepack, self.subject)

            # then use the parents details
            set_childs_persistentIdentity(triplepack, parent, self.subject)
            set_childs_version(triplepack, parent, self.subject)

        elif not is_SBOL_Compliant(triplepack, self.subject):
            if get_SBOL_persistentIdentity(triplepack, self.subject) is None:
                pId = Uri(self.subject.uri)
                triplepack.add((self.subject, persistentIdentity, pId))


        new_id = set_identity(triplepack, self.subject)
        subjects[subjects.index(self.subject)] = new_id

        return triplepack

def is_valid_parameters(identifiers, triplepack, subjects):
    #print(triplepack)
    return True

def get_identifier_uris(paths):
    name = "identifiers.shb"
    identifier_path = None
    for path in paths:
        for root, dirs, files in os.walk(path):
            if name in files:
                identifier_path = os.path.join(root, name)
                break
    if identifier_path is None:
        raise FileNotFoundError(f"Can't find file {name} for SBOL identifier extension")

    identifiers = {}
    data = open(identifier_path,"r")
    lines = data.readlines()[1:]
    cur_template_types = []
    cur_template_property = ""
    for line in lines:
        if "=" not in line and "#" not in line:
            continue
        else:
            line = line.replace(" ", "").replace("\n","")
            if line[0] == "#":
                template_types = line.split("(")[1].split(")")[0].split(",")
                template_property = line.split(")")[1]
                for template_type in template_types:
                    if template_type not in identifiers.keys():
                        identifiers[template_type]= {}
                    identifiers[template_type][template_property] = []
                    cur_template_types = template_types
                    cur_template_property = template_property

            if line[0] != "#" and "=" in line:
                name = line.split("=")[0]
                for cur_template_type in cur_template_types:
                    identifiers[cur_template_type][cur_template_property].append(name)
                    
    data.close()
    return identifiers

def is_SBOL_Compliant(triplepack, uri):
    version = get_SBOL_version(triplepack, uri)
    dId = get_SBOL_displayId(triplepack, uri)
    pId = get_SBOL_persistentIdentity(triplepack, uri)

    compliant = dId is not None and pId is not None
    compliant = compliant and uri.uri == pId.uri + "/" + str(version.value)
    if is_SBOL_TopLevel(triplepack, uri):
        compliant = compliant and pId.split()[-1] == dId.value
    return compliant


def set_identity(triplepack, uri):
    version = get_SBOL_version(triplepack, uri)
    if version is not None:
        pid = get_SBOL_persistentIdentity(triplepack, uri)
        new_id = Uri(pid.uri + '/' + str(version.value))
        triplepack.replace_with_type(uri, new_id, persistentIdentity)
    else:
        new_id = get_SBOL_persistentIdentity(triplepack, uri)
        triplepack.replace_with_type(uri, new_id, persistentIdentity)
    return new_id


def set_childs_persistentIdentity(triplepack, parent, child):
    parents_pId = get_SBOL_persistentIdentity(triplepack, parent)
    childs_dId = get_SBOL_displayId(triplepack, child)
    p = parents_pId.split()[-1]
    childs_pId = Uri(parents_pId.uri + '/' + childs_dId.value.replace(p,""))
    triplepack.set(child, persistentIdentity, childs_pId)


def set_childs_version(triplepack, parent, child):
    parents_version = get_SBOL_version(triplepack, parent)
    if parents_version is not None:
        triplepack.set(child, version, parents_version)


def get_possible_SBOL_types(triplepack, uri):
    '''
    Return the possible SBOL object types based on the RDF.type
    property attached to uri.

    '''
    return {o for (s, p, o) in triplepack.search((uri, rdf_type, None))}


def is_SBOL_TopLevel(triplepack, uri):
    '''
    Checks if SBOL object named by uri is a TopLevel SBOL object.
    '''
    the_types = get_possible_SBOL_types(triplepack, uri)
    return any([t in toplevels for t in the_types])


def get_SBOL_parent(triplepack, child):
    '''
    Search the triplepack for the unique parent of the child, that is,
    the unique subject that is related to the child by one of the
    ownership predicates, or by the component predicate if the parent
    is a ComponentDefinition

    If more than one parent is found or the child is not a TopLevel
    SBOL object and no parent is found, an SBOLComplianceError is
    raised.

    If the child is an SBOL TopLevel object, then None is returned. 
    '''
    possible_parents = set()

    for predicate in ownership_predicates:
        possible_parents |= {s for (s, p, o)
                             in triplepack.search((None, predicate, child))}

    # now for the components
    component = Uri(sbolns.uri + 'component')
    cd = Uri(sbolns.uri + 'ComponentDefinition')
    sa = Uri(sbolns.uri + 'SequenceAnnotation')
    possible_parents |= {s for (s, p, o)
                         in triplepack.search((None, component, child))
                         if cd in get_possible_SBOL_types(triplepack, s)
                         and sa not in get_possible_SBOL_types(triplepack, s)}

    # at this point we should have the parent/s
    if len(possible_parents) > 1:
        raise SBOLComplianceError(f"{child} has multiple SBOL parents\n" +
                                  f"Which are:\n" +
                                  f"{','.join(map(str, possible_parents))}")

    elif not possible_parents and not is_SBOL_TopLevel(triplepack, child):
        raise SBOLComplianceError(f"{child} is an orphaned SBOL child")

    elif possible_parents and is_SBOL_TopLevel(triplepack, child):
        raise SBOLComplianceError(f"{child} is a TopLevel SBOL object\n" +
                                  f"But has parents:\n" +
                                  f"{','.join(map(str, possible_parents))}")

    parent = possible_parents.pop() if possible_parents else None
    return parent


def get_SBOL_version(triplepack, uri):
    matches = {o for (s, p, o)
               in triplepack.search((uri, version, None))}
    if len(matches) > 1:
        raise SBOLComplianceError(f"{uri} has multiple version's.")
    elif not matches:
        return None
    else:
        return matches.pop()


def get_SBOL_persistentIdentity(triplepack, uri):
    matches = {o for (s, p, o)
               in triplepack.search((uri, persistentIdentity, None))}
    if len(matches) > 1:
        raise SBOLComplianceError(f"{uri} has multiple persistentIdentity's.")
    elif not matches:
        return None
    else:
        return matches.pop()


def get_SBOL_displayId(triplepack, uri):
    matches = {o for (s, p, o) in triplepack.search((uri, displayId, None))}
    if len(matches) > 1:
        raise SBOLComplianceError(f"{uri} has multiple displayId's.")
    elif not matches:
        return None
    else:
        return matches.pop()


class SBOLComplianceError(ExtensionError):

    def __init__(self, helpful_message):
        self._type = 'SBOL2 Compliant URI error'
        self._helpful_message = helpful_message

    def __str__(self):
        return ExtensionError.__str__(self) + format(" %s\n" % self._helpful_message)


import rdflib
import os
from .logic import And
from .error import ExtensionError
from rdfscript.core import Uri, Value
from sbol_rdf_identifiers import identifiers

class SBOL2:
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

    def run(self, triplepack,env):
        subjects = list(triplepack.subjects)
        identifiers.swap_version("sbol_2")
        for i in range(len(subjects)):
            SBOLCompliant(subjects[i]).run(triplepack, subjects)

        validate(subjects,triplepack)

        return triplepack


class SBOLCompliant:
    '''
    Extension to check a single subject, naming an SBOL object, has an
    SBOL compliant URI, and if not, attempts to modify triplepack such
    that they are.
    '''
    def __init__(self, for_subject):
        self.subject = for_subject

    def run(self, triplepack, subjects):
        parent = get_SBOL_parent(triplepack, self.subject)
        # Everything has a display id
        if not triplepack.search((self.subject, identifiers.predicates.display_id, None)):
            new_displayId = self.subject.split()[-1]
        
            triplepack.add((self.subject, identifiers.predicates.display_id, Value(new_displayId)))
        # Everything has a Version
        if get_SBOL_version(triplepack, self.subject) is None:
            #Set default version of 1.
            triplepack.add((self.subject, identifiers.predicates.version, Value("1")))



        if parent is not None:
            # its a child
            if not triplepack.has(parent, identifiers.predicates.persistent_identity):
                SBOLCompliant(parent).run(triplepack, subjects)

            # parent uri might have changed!!!
            parent = get_SBOL_parent(triplepack, self.subject)

            # then use the parents details
            set_childs_persistentIdentity(triplepack, parent, self.subject)
            set_childs_version(triplepack, parent, self.subject)

        elif not is_SBOL_Compliant(triplepack, self.subject):
            if get_SBOL_persistentIdentity(triplepack, self.subject) is None:
                pId = Uri(self.subject.uri)
                triplepack.add((self.subject, identifiers.predicates.persistent_identity, pId))


        new_id = set_identity(triplepack, self.subject)
        subjects[subjects.index(self.subject)] = new_id

        return triplepack


def validate(subjects, triplepack):
    '''
    Built-in validator to made checks on the graph to ensure Valid SBOL.
    '''

    symbols_table = triplepack.bindings
    ids = get_identifier_uris(triplepack._paths)
    for subject in subjects:
        triples = triplepack.search((subject,None,None))
        for s,p,o in triples:
            if p in identifiers.predicates.template_predicates and o not in subjects:
                raise SBOLComplianceError(f"Unknown Parameter for {s}")

    return


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
        triplepack.replace_with_type(uri, new_id, identifiers.predicates.persistent_identity)
    else:
        new_id = get_SBOL_persistentIdentity(triplepack, uri)
        triplepack.replace_with_type(uri, new_id, identifiers.predicates.persistent_identity)
    return new_id


def set_childs_persistentIdentity(triplepack, parent, child):
    parents_pId = get_SBOL_persistentIdentity(triplepack, parent)
    childs_dId = get_SBOL_displayId(triplepack, child)
    childs_pId = Uri(parents_pId.uri + '/' + childs_dId.value)
    triplepack.set(child, identifiers.predicates.persistent_identity, childs_pId)


def set_childs_version(triplepack, parent, child):
    parents_version = get_SBOL_version(triplepack, parent)
    if parents_version is not None:
        triplepack.set(child, identifiers.predicates.version, parents_version)


def get_possible_SBOL_types(triplepack, uri):
    '''
    Return the possible SBOL object types based on the RDF.type
    property attached to uri.

    '''
    return {o for (s, p, o) in triplepack.search((uri, identifiers.predicates.rdf_type, None))}


def is_SBOL_TopLevel(triplepack, uri):
    '''
    Checks if SBOL object named by uri is a TopLevel SBOL object.
    '''
    the_types = get_possible_SBOL_types(triplepack, uri)
    return any([t in identifiers.objects.top_levels for t in the_types])


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

    for predicate in identifiers.predicates.ownership_predicates:
        possible_parents |= {s for (s, p, o)
                             in triplepack.search((None, predicate, child))}

    # now for the components

    possible_parents |= {s for (s, p, o)
                         in triplepack.search((None, identifiers.predicates.component, child))
                         if identifiers.objects.component_definition in get_possible_SBOL_types(triplepack, s)
                         and identifiers.objects.sequence_annotation not in get_possible_SBOL_types(triplepack, s)}

    if child in possible_parents:
        raise SBOLComplianceError(f'{child} is its own possible parent, likely due to being a property of itself')
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
               in triplepack.search((uri, identifiers.predicates.version, None))}
    if len(matches) > 1:
        raise SBOLComplianceError(f"{uri} has multiple version's.")
    elif not matches:
        return None
    else:
        return matches.pop()


def get_SBOL_persistentIdentity(triplepack, uri):
    matches = {o for (s, p, o)
               in triplepack.search((uri, identifiers.predicates.persistent_identity, None))}
    if len(matches) > 1:
        raise SBOLComplianceError(f"{uri} has multiple persistentIdentity's.")
    elif not matches:
        return None
    else:
        return matches.pop()


def get_SBOL_displayId(triplepack, uri):
    matches = {o for (s, p, o) in triplepack.search((uri, identifiers.predicates.display_id, None))}
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

    def simplified_error_message(self):
        return f'{self._helpful_message}'


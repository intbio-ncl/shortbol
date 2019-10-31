import rdflib
import pdb

from .logic import And
from .error import ExtensionError
from rdfscript.core import Uri, Value

_sbolns = Uri('http://sbols.org/v2#', None)
_toplevels = set([Uri(_sbolns.uri + tl, None) for tl
                  in ['Sequence',
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
                      'CombinatorialDerivation']])

ownership_predicates = set([Uri(_sbolns.uri + tl, None) for tl
    in ['component',
        'module',
        'mapsTo',
        'interaction',
        'participation',
        'functionalComponent',
        'sequenceConstraint']])

_sbol_pId = Uri(_sbolns.uri + 'persistentIdentity', None)
_sbol_dId = Uri(_sbolns.uri + 'displayId', None)
_sbol_version = Uri(_sbolns.uri + 'version', None)
_rdf_type = Uri(rdflib.RDF.type, None)


class SbolIdentity:
    '''
    Class to check all objects are SBOL compliant.
    '''

    def __init__(self):
        pass

    def run(self, triplepack):
        #Creates logic.And() instance which takes Language Objects and then calls And.run() which in turn calls run on all SBOLCompliant Objects
        #Simply makes a SBOLCompliant Object for each form in graph and calls run.
        return And(*[SBOLCompliant(s) for s in triplepack.subjects]).run(triplepack)


class SBOLCompliant:
    '''
    Class to check a single object is SBOL compliant.
    '''
    def __init__(self, for_subject):
        self._subject = for_subject

    def run(self, triplepack):
        # Creates a new TriplePack Object 
        subpack = triplepack.sub_pack(self._subject)
        if SBOLcheckTopLevel(subpack):
            SBOLCompliantTopLevel(self._subject).run(triplepack)
        else:
            SBOLCompliantChild(self._subject).run(triplepack)

        return triplepack


class SBOLCompliantTopLevel:
    '''
    Class to check if a toplevel component is SBOL compliant
    '''
    def __init__(self, for_subject):
        self._subject = for_subject

    def run(self, triplepack):
        # Top level Object URI's : BaseName/ObjectType/ObjectName/Version
        # Need to add Object Type to Base URI then Version @@@@
          
        #Validate TopLevel Object, Does it have persistentID, DisplayID and Version?
        if not triplepack.has(self._subject, _sbol_pId): 
            #Persistent ID = Object URI without version Number
            pId = Uri(self._subject.uri, None)
            triplepack.set(self._subject, _sbol_pId, pId)

        if not triplepack.has(self._subject, _sbol_dId):
            #Set display ID as object name (Dirty splicing URI)
            dId = Value(self._subject.split()[-1])
            triplepack.set(self._subject, _sbol_dId, dId)

        if not triplepack.has(self._subject, _sbol_version):
            #Set Default Version Number (1)
            default_version = Value("1")
            triplepack.set(self._subject, _sbol_version, default_version)



class SBOLCompliantChild:
    '''
    Check if any Child/Non TopLevel objects are Valid SBOL.
    '''
    def __init__(self, for_subject):
        self._subject = for_subject

    def run(self, triplepack):
        '''
        A SBOLCompliantChild is compliant when:
            Has atleast one Parent. (This technicially should always be true for Non-TopLevel Objects)
            If there is more than one parent parents must be a valid combination??
            Must have a persistentID (If not set make one)
            
        '''
        subpack = triplepack.sub_pack(self._subject)
        parent = SBOLParent(triplepack, self._subject)



        # Child Object URI's : BaseName/ObjectType/ObjectName/Version
        # Need to add Object Type to Base URI then Version @@@@
        if not triplepack.has(parent, _sbol_pId):
            SBOLCompliant(parent).run(triplepack)

        #Validate Child Object, Does it have persistentID, DisplayID and Version?
        if not triplepack.has(self._subject, _sbol_dId):
            #Set display ID as object name (Dirty, splicing URI)
            dId = Value(self._subject.split()[-1])
            triplepack.set(self._subject, _sbol_dId, dId)
            subpack.set(self._subject, _sbol_dId, Value(dId))

        if not triplepack.has(self._subject, _sbol_version):
            #Check if parent has a version and use that.
            if triplepack.has(parent, _sbol_version):
                triplepack.set(self._subject,_sbol_version,triplepack.value(parent, _sbol_version))
            else:
                #Set Default Version Number (1)
                default_version = Value("1")
                triplepack.set(self._subject, _sbol_version, default_version)


            #Persistent ID = Base URI + TopLevelURI + Child URI. without version Number and any intermediate Parent Objects (That arent TOP level)
            parentpid = triplepack.value(parent, _sbol_pId)
            pId = Uri(parentpid.uri + '/' + self._subject.split()[-1])
            triplepack.set(self._subject, _sbol_pId, pId)

class SBOLComplianceError(ExtensionError):

    def __init__(self, helpful_message):
        self._type = 'SBOL2 Compliant URI error'
        self._helpful_message = helpful_message

    def __str__(self):
        return ExtensionError.__str__(self) + format(" %s\n" % self._helpful_message)


def SBOLversion(triplepack):
    return triplepack.value(_sbol_version)


def SBOLpId(triplepack):
    return triplepack.value(_sbol_pId)


def SBOLdId(triplepack):
    return triplepack.value(_sbol_dId)


def SBOLcheckIdentity(triplepack):
    identity = triplepack.subjects.pop()
    if SBOLversion(triplepack):
        return identity.split()[-1] == triplepack.value(_sbol_version).value
    else:
        return True


def SBOLParent(triplepack, child):
    '''
    Find any parents by searching triples with child object and checking for matches.
    '''
    with_child_as_object = triplepack.search((None, None, child))
    possible_parents = set([s for (s, p, o) in with_child_as_object if p in ownership_predicates])
    if len(possible_parents) > 1:
        message = format("The SBOL object %s should only have one parent object."
                         % child)
        raise SBOLComplianceError(message)
    elif len(possible_parents) == 1:
        return possible_parents.pop()
    else:
        message = format("The SBOL object %s does not have a parent object."
                         % child)
        raise SBOLComplianceError(message)


def SBOLcheckTopLevel(triplepack):
    '''
    Checks if triple is a toplevel object.
    Done by checking if type is in top_levels list.
    '''
    _type = triplepack.value(_rdf_type)
    if isinstance(_type, list):
        return any([t in _toplevels for t in _type])
    else:
        return _type in _toplevels

    
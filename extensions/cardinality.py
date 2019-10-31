import rdflib
from .error import ExtensionError

class AtLeastOne:

    def __init__(self, property_uri):
        self._prop = property_uri

    def run(self, triplepack):

        subjects = triplepack.subjects
        if len(subjects) > 0:
            for subject in subjects:
                if not triplepack.has(subject, self._prop):
                    raise CardinalityError(self._prop, 'at least 1', '0')
        else:
            raise CardinalityError(self._prop, 'at least 1', '0')

        return triplepack

class ExactlyOne:

    def __init__(self, property_uri):
        self._prop = property_uri

    def run(self, triplepack):

        subjects = triplepack.subjects
        if len(subjects) > 0:
            for subject in subjects:
                if not triplepack.has_unique(subject, self._prop):
                    number_found = len(triplepack.search((subject, self._prop, None)))
                    raise CardinalityError(self._prop, 'exactly 1', number_found)
        else:
            raise CardinalityError(self._prop, 'at least 1', '0')

        return triplepack

class ExactlyN:

    def __init__(self, property_uri, n):
        self._prop = property_uri
        self._n = n
        self._exactly_n = format("exactly %s" % n)

    def run(self, triplepack):

        subjects = triplepack.subjects
        if len(subjects) > 0:
            for subject in subjects:
                number_found = len(triplepack.search((subject, self._prop, None)))
                if not number_found == self._n:
                    raise CardinalityError(self._prop, self._exactly_n, number_found)
        else:
            raise CardinalityError(self._prop, self._exactly_n, 0)

        return triplepack

class CardinalityError(ExtensionError):

    def __init__(self, predicate, expected, actual):
        ExtensionError.__init__(self)
        self._type = 'Cardinality restriction violation'
        self._predicate = predicate
        self._expected = expected
        self._actual = actual

    def __str__(self):
        return (ExtensionError.__str__(self) +
                format(" Expected %s value(s) for %s, but actually got %s\n"
                       % (self._expected, self._predicate, self._actual)))

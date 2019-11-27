import rdflib
import re

from .error import (PrefixError,
                    UnexpectedType)


class Node:
    """Language object."""

    def __init__(self, location):
        """
        location is a Location object representing this language
        object's position in the source code.
        """
        self._location = location

    @property
    def location(self):
        return self._location

    @property
    def line(self):
        return self._location.line

    @property
    def col(self):
        return self._location.col

    @property
    def file(self):
        return self._location.filename


class Name(Node):

    def __init__(self, *names, location=None):
        super().__init__(location)
        self.names = list(names)

    def __eq__(self, other):
        return (isinstance(other, Name) and self.names == other.names or
                isinstance(other, Self) and self.names == [Self()])

    def __str__(self):
        return ':'.join([str(name) for name in self.names])

    def __repr__(self):
        return f"[NAME: {self.names}]"

    def is_prefixed(self, context):
        if len(self.names) > 1 and isinstance(self.names[0], str):
            try:
                return context.uri_for_prefix(self.names[0])
            except PrefixError:
                return False
        else:
            return False

    def evaluate(self, context):

        uri = Uri(context.uri, location=self.location)

        for n in range(0, len(self.names)):
            if isinstance(self.names[n], Self):
                current_self = context.current_self
                if isinstance(current_self, Uri):
                    if n > 0:
                        uri.extend(context.current_self, delimiter='')
                    else:
                        uri = Uri(current_self, location=self.location)
                elif isinstance(current_self, Name):
                    rest = current_self.names + self.names[n + 1:]
                    if n > 0:
                        return Name(uri, *rest, location=self.location)
                    else:
                        return Name(*rest, location=self.location)
            elif isinstance(self.names[n], Uri):
                if n > 0:
                    uri.extend(self.names[n], delimiter='')
                else:
                    uri = Uri(self.names[n])
            elif isinstance(self.names[n], str):
                if n == 0 and self.is_prefixed(context):
                    uri = self.is_prefixed(context)
                else:
                    uri.extend(Uri(self.names[n]), delimiter='')

            lookup = context.lookup(uri)
            if lookup is not None:
                if isinstance(lookup, Uri):
                    uri = Uri(lookup, location=self.location)
                elif n == len(self.names) - 1:
                    uri = lookup

        return uri


class Parameter(Name):

    def __init__(self, name_string, position, location=None):
        super().__init__(name_string, location=location)
        self.position = position

    def __repr__(self):
        return f"[PARAMETER: {self.names[0]}]"

    def substitute(self, possible_parameter):
        result = possible_parameter
        if isinstance(possible_parameter, Name):
            def replace(x):
                result = self if self.names[0] == x else x
                return result

            new_names = map(replace, possible_parameter.names)
            result = Name(*new_names, location=possible_parameter.location)

        return result

    def evaluate(self, env):
        return self


class Self(Parameter):

    def __init__(self, location=None):
        super().__init__('self', -1, location=location)

    def __str__(self):
        return "self"

    def __repr__(self):
        return format("[SELF]")

    def evaluate(self, context):
        return context.current_self


class Uri(Node):
    """Language object for a URI."""

    def __init__(self, uri, location=None):
        """
        uri can be one of:
          - string
          - rdflib.URIRef object
          - Uri object

        uri is converted to a string
        """
        super().__init__(location)
        if isinstance(uri, rdflib.URIRef):
            self._uri = uri.toPython()
        elif isinstance(uri, Uri):
            self._uri = uri.uri
        else:
            self._uri = uri

    def __eq__(self, other):
        return (isinstance(other, Uri) and
                self.uri == other.uri)

    def __str__(self):
        return '<' + self.uri + '>'

    def __repr__(self):
        return format("[URI: %s]" % self._uri)

    def __hash__(self):
        return self.uri.__hash__()

    @property
    def uri(self):
        return self._uri

    def extend(self, other, delimiter='#'):
        self._uri = self.uri + delimiter + other.uri

    def split(self):
        return re.split('#|/|:', self.uri)

    def evaluate(self, context):
        return self


class Value(Node):
    """Language object for an RDF literal."""

    def __init__(self, python_literal, location=None):

        Node.__init__(self, location)
        self.value = python_literal

    def __eq__(self, other):
        return (isinstance(other, Value) and
                type(self.value) == type(other.value) and
                self.value == other.value)

    def __str__(self):
        return format("%r" % self.value)

    def __repr__(self):
        return format("[VALUE: %s]" % self.value)

    def __hash__(self):
        return self.value.__hash__()

    def evaluate(self, context):
        return self


class Argument(Value):

    def __init__(self, value_expr, position, location=None):
        super().__init__(location)
        self.value = value_expr
        self.position = position

    def __str__(self):
        return f"{self.value}"

    def __repr__(self):
        return f"[RDFscript ARG: {self.value}]"

    def marshal(self, param):
        if isinstance(param, Parameter) and param.position == self.position:
            return self
        else:
            return param


class Assignment(Node):

    def __init__(self, name, value, location=None):
        super().__init__(location)
        self.name = name
        self.value = value

    def __eq__(self, other):
        return (isinstance(other, Assignment) and
                self.name == other.name and
                self.value == other.value)

    def __str__(self):
        return f"{self.name} = {self.value}"

    def __repr__(self):
        return f"[ASSIGN: {self.name} = {self.value}]"

    def evaluate(self, context):
        uri = self.name.evaluate(context)
        if not isinstance(uri, Uri):
            raise UnexpectedType(Uri, uri, self.location)

        value = self.value.evaluate(context)

        context.assign(uri, value)
        return value

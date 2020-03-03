import rdflib
import re

from .error import PrefixError
from .error import UnexpectedType


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


class Identifier(Node):
    def __init__(self, *parts, location=None):
        super().__init__(location)
        self.parts = list(parts)

    def __eq__(self, other):
        return isinstance(other, Identifier) and self.parts == other.parts

    def __str__(self):
        return ':'.join([str(part) for part in self.parts])

    def __repr__(self):
        return f"[Identifier: {self.parts}]"

    def __iter__(self):
        return iter(self.parts)

    def __len__(self):
        return len(self.parts)

    def evaluate(self, env):
        return self

    def prefixify(self, context):
        uri = context.uri

        if context.prefix is not None:
            uri = context.uri_for_prefix(context.prefix)

        try:
            uri = context.uri_for_prefix(self.parts[0].name)
            self.parts[0] = uri
        except PrefixError:
            self.parts.insert(0, uri)

        return self
    
    def flatten(self):
        flat_list = []
        for part in self.parts:
            if isinstance(part,Identifier):
                flat_list += part.parts
            else:
                flat_list.append(part)
        return Identifier(*flat_list,location=self.location)


    def evaluate(self, context):
        if not isinstance(self.parts[0], (Uri, Parameter)):
            self.prefixify(context)

        uri = Uri('')

        for i, part in enumerate(self.parts):
            try:
                uri = uri + part.evaluate(context)

                binding = context.lookup(uri)
                if binding is not None and i == len(self) - 1 :
                    uri = binding
                elif isinstance(binding, Uri):
                    uri = binding
                    
            except TypeError:
                new_parts = self.parts if uri == Uri('') else [uri, *self.parts[i:]]
                return Identifier(*new_parts, location=self.location)

        return uri


class Name(Node):
    def __init__(self, name_string, location=None):
        super().__init__(location=location)
        self.name = name_string

    def __eq__(self, other):
        return isinstance(other, Name) and self.name == other.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"[Name: {self.name}]"

    def evaluate(self, context):
        return Uri(self.name, location=self.location)


class Parameter(Name):

    def __init__(self, name_string, position, location=None):
        super().__init__(name_string, location=location)
        self.position = position

    def __repr__(self):
        return f"[PARAMETER: {self.name}]"

    def __eq__(self, other):
        return isinstance(other, Parameter) and self.name == other.name

    def substitute(self, possible_parameter):
        result = possible_parameter
        if isinstance(possible_parameter, Identifier):
            def replace(x):
                if isinstance(x, Name) and self.name == x.name:
                    # Substitution
                    return self
                else:
                    return x 

            new_names = [replace(part) for part in possible_parameter.parts]
            result = Identifier(*new_names, location=possible_parameter.location)

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
        return self


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
            self.uri = uri.toPython()
        elif isinstance(uri, Uri):
            self.uri = uri.uri
        else:
            self.uri = uri

    def __eq__(self, other):
        return isinstance(other, Uri) and self.uri == other.uri

    def __str__(self):
        return f"<{self.uri}>"

    def __repr__(self):
        return f"[URI: {self.uri}]"

    def __hash__(self):
        return self.uri.__hash__()

    def __add__(self, other):
        if not isinstance(other, Uri):
            raise TypeError(f"Parameter mismatch at {self.location} with parameter name: {other}")

        return Uri(self.uri + other.uri)

    def extend(self, other, delimiter='#'):
        self.uri = self.uri + delimiter + other.uri

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
        result = param
        def replace(x):
            if isinstance(x, Parameter) and self.position == x.position:
                # Substitution
                return self.value
            else:
                return x
                    
        if isinstance(param, Identifier):
            if isinstance(self.value, (Uri, Name, Parameter)):
                new_parts = [replace(part) for part in param.parts]
                result = Identifier(*new_parts, location=param.location)
            elif len(param.parts) == 1 and isinstance(param.parts[0], Parameter) and param.parts[0].position == self.position:
                result = self.value
            elif isinstance(self.value,Identifier) and len(param.parts) > 1:
                param_parts = param.parts
                new_parts = []
                for n in param_parts:
                    #self.value.parts
                    new_parts.append(replace(n))
                result =  Identifier(*new_parts, location=param.location).flatten()

        return result


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

from .core import Node, Name, Self, Parameter, Identifier
from .pragma import ExtensionPragma
from .expansion import Expansion


class Template(Node):
    def __init__(self, identifier, parameters, body, location=None):
        super().__init__(location)
        self.identifier = identifier
        self.parameters = []
        for pos, param in enumerate(parameters):
            self.parameters.append(Parameter(param, pos, location))
        self.parameters.insert(0, Self())

        self.extensions = []
        self.body = []
        for statement in body:
            if isinstance(statement, ExtensionPragma):
                self.extensions.append(statement)
            else:
                self.body.append(statement)

    def __eq__(self, other):
        return (isinstance(other, Template) and
                self.identifier == other.identifier and
                self.parameters == other.parameters and
                self.body == other.body)

    def __repr__(self):
        return f"[TEMPLATE: {self.identifier}, {self.parameters}, {self.body}]"

    def __str__(self):
        return (f"{self.identifier}({','.join(map(str, self.parameters))})" +
                f"({chr(10).join(map(str, self.body))})")

    def as_triples(self, context):
        triples = []

        for statement in self.body:
            triples += statement.as_triples(context)

        def parameter_substitution(triple):
            result = triple
            for parameter in self.parameters:
                result = tuple([parameter.substitute(x) for x in result])

            return result

        triples = [parameter_substitution(triple) for triple in triples]

        return list(triples)

    def store_triples(self, context):
        triples = self.as_triples(context)

        def triple_eval(triple):
            (s, p, o) = triple
            return (s.evaluate(context),
                    p.evaluate(context),
                    o.evaluate(context))

        try:
            evaluated_triples = [triple_eval(triple) for triple in triples]
        except AttributeError as e:
            print(triples)
            raise AttributeError(e)


        uri = self.identifier.evaluate(context)
        context.assign_template(uri, evaluated_triples)

        return evaluated_triples

    def collect_extensions(self, context):
        collected = self.extensions

        for statement in self.body:
            if isinstance(statement, Expansion) and statement.identifier is None:
                collected += statement.get_extensions(context)

        return collected

    def store_extensions(self, context):
        extensions = self.collect_extensions(context)
        for ext in extensions:
            ext.substitute_params(self.parameters)

        extensions = [ext.evaluate(context) for ext in extensions]

        uri = self.identifier.evaluate(context)
        context.assign_extensions(uri, extensions)

        return extensions

    def evaluate(self, context):
        old_self = context.uri
        context.current_self = Identifier(Self())

        self.store_triples(context)
        self.store_extensions(context)

        context.current_self = old_self

        return self.identifier.evaluate(context)


class Property(Node):

    def __init__(self, identifier, value, location=None):

        Node.__init__(self, location)
        self.identifier = identifier
        self.value = value

    def __eq__(self, other):
        return (isinstance(other, Property) and
                self.identifier == other.identifier and
                self.value == other.value)

    def __str__(self):
        return format("%s = %s\n" % (self.identifier, self.value))

    def __repr__(self):
        return format("%s = %s\n" % (self.identifier, self.value))


    def substitute_params(self, parameters):

        for parameter in parameters:
            if parameter.is_substitute(self.identifier):
                self.identifier = parameter
            if parameter.is_substitute(self.value):
                self.value = parameter

    def as_triples(self, context):
        triples = []
        if isinstance(self.value, Expansion):
            triples += self.value.as_triples(context)
            triples += [(Identifier(Self()),
                         self.identifier,
                         self.value.identifier)]
            return triples
        else:
            return [(Identifier(Self()),
                     self.identifier,
                     self.value)]


def evaluate_triples(triples, context):

    def evaluate_triple(triple):
        (s, p, o) = triple
        return (s.evaluate(context),
                p.evaluate(context),
                o.evaluate(context))

    results = [evaluate_triple(triple) for triple in triples]

    return results


def expand_expansion_in_triples(triples, context):
    new_triples = []

    def expand(thing):
        extra_triples = []
        if isinstance(thing, Expansion):
            extra_triples += thing.as_triples(context)
            thing = thing.identifier

        return extra_triples

    for triple in triples:
        (s, p, o) = triple
        new_triples += expand(s)
        new_triples += expand(p)
        new_triples += expand(o)
        new_triples.append((s, p, o))

    return new_triples

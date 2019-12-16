from rdfscript.core import Argument, Identifier, Name, Node, Self, Uri
from rdfscript.pragma import ExtensionPragma
from rdfscript.error import TemplateNotFound


class Expansion(Node):
    def __init__(self, identifier, template, args, body, location=None):
        super().__init__(location)
        self.template = template
        self.identifier = identifier
        self.args = [] if identifier is None else [Argument(identifier, -1)]
        for n in range(0, len(args)):
            arg = args[n]
            if isinstance(arg, Argument):
                self.args.append(Argument(arg.value, n, location))
            else:
                self.args.append(Argument(arg, n, location))

        self.extensions = []
        self.body = []
        for statement in body:
            if isinstance(statement, ExtensionPragma):
                for arg in self.args:
                    ext_args = [arg.marshal(ext_arg) for ext_arg in statement.args]
                self.extensions.append(ExtensionPragma(statement.name, ext_args))
            else:
                self.body.append(statement)

    def __eq__(self, other):
        return (isinstance(other, Expansion) and
                self.template == other.template and
                self.identifier == other.identifier and
                self.args == other.args and
                self.body == other.body)

    def __repr__(self):
        return format("%s is a %s(%s)\n  (%s)\n" %
                      (self.identifier, self.template, self.args, self.body))

    def get_extensions(self, context):
        template_uri = self.template.evaluate(context)

        raw_extensions = context.lookup_extensions(template_uri)
        processed_extensions = []
        for ext in raw_extensions:
            ext_args = ext.args
            for arg in self.args:
                ext_args = [arg.marshal(ext_arg) for ext_arg in ext_args]
            processed_extensions += [ExtensionPragma(ext.name, ext_args)]

        return processed_extensions + self.extensions

    def as_triples(self, context):
        template_uri = self.template.evaluate(context)
        try:
            triples = context.lookup_template(template_uri)
        except KeyError:
            raise TemplateNotFound(template_uri, self.template.location)

        for statement in self.body:
            triples += statement.as_triples(context)

        def argument_marshal(triple):
            result = triple
            for argument in self.args:
                result = tuple(map(lambda x: argument.marshal(x), result))

            return result

        triples = map(argument_marshal, triples)

        return triples

    def evaluate(self, context):
        identifier = self.identifier.evaluate(context)
        evaluated_args = []
        for arg in self.args:
            evaluated_arg = Argument(arg.value.evaluate(context), arg.position)
            evaluated_args.append(evaluated_arg)

        triples = self.as_triples(context)

        def evaluate_triple(triple):
            return tuple(map(lambda x: x.evaluate(context), triple))

        triples = map(evaluate_triple, triples)

        for ext in self.get_extensions(context):
            triples = ext.run(context, triples)

        context.add_triples(triples)

        return identifier


def replace_self(triples, replace_with):
    result = []
    for triple in triples:
        (s, p, o) = triple
        if isinstance(s, Identifier):
            s = replace_self_in_identifier(s, replace_with)
        if isinstance(p, Identifier):
            p = replace_self_in_identifier(p, replace_with)
        if isinstance(o, Identifier):
            o = replace_self_in_identifier(o, replace_with)

        result.append((s, p, o))

    return result

#Maybe replace_self tests are written incorrectly and input for expansion tests are wrong.
def replace_self_in_identifier(identifier, _with):
    parts = identifier.parts
    new_names = []
    for part in parts:
        # If Identifier then add parts?
        if part == Self() and isinstance(_with, Identifier):
            new_names += _with.parts
        #Anything else we can just add?  
        elif part == Self():
            new_names.append(_with)
        else:
            new_names.append(part)

    return Identifier(*new_names, location=identifier.location)

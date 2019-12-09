from rdfscript.core import Node, Argument, Name, Self, Identifier
from rdfscript.pragma import ExtensionPragma
from rdfscript.error import TemplateNotFound


class Expansion(Node):

    def __init__(self, identifier, template, args, body, location=None):

        super().__init__(location)
        self.template = template
        self.identifier = identifier
        self.args = []
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
                self.extensions.append(statement)
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

        old_self = context.current_self
        context.current_self = self.identifier

        for statement in self.body:
            triples += statement.as_triples(context)

        def argument_marshal(triple):
            result = triple
            for argument in self.args:
                result = tuple(map(lambda x: argument.marshal(x), result))

            return result

        triples = map(argument_marshal, triples)

        if self.identifier is not None:
            triples = replace_self(triples, self.identifier)

        context.current_self = old_self

        return triples

    def evaluate(self, context):
        identifier = self.identifier.evaluate(context)

        triples = self.as_triples(context)
        old_self = context.current_self
        context.current_self = identifier

        def evaluate_triple(triple):
            return tuple(map(lambda x: x.evaluate(context), triple))

        triples = map(evaluate_triple, triples)

        for ext in self.get_extensions(context):
            triples = ext.run(context, triples)

        context.current_self = old_self

        context.add_triples(triples)

        return identifier


def replace_self(triples, replace_with):
    result = []
    for triple in triples:
        (s, p, o) = triple
        if isinstance(s, Identifier):
            s = replace_self_in_name(s, replace_with)
        if isinstance(p, Identifier):
            p = replace_self_in_name(p, replace_with)
        if isinstance(o, Identifier):
            o = replace_self_in_name(o, replace_with)

        result.append((s, p, o))

    return result

def replace_self_in_name(old_name, _with):
    names = old_name.parts
    new_names = []
    for name in names:
        if name == Self() and isinstance(_with, Identifier):
            new_names += _with.parts
        elif name == Self():
            new_names.append(_with)
        else:
            new_names.append(name)

    return Identifier(*new_names, location=old_name.location)

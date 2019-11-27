from rdfscript.core import Node, Argument, Name, Self
from rdfscript.pragma import ExtensionPragma
from rdfscript.error import TemplateNotFound


class Expansion(Node):

    def __init__(self, name, template, args, body, location=None):

        super().__init__(location)
        self.template = template
        self.name = name
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
                self.name == other.name and
                self.args == other.args and
                self.body == other.body)

    def __repr__(self):
        return format("%s is a %s(%s)\n  (%s)\n" %
                      (self.name, self.template, self.args, self.body))

    def get_extensions(self, env):
        template_uri = self.template.evaluate(env)

        raw_extensions = env.lookup_extensions(template_uri)
        processed_extensions = []
        for ext in raw_extensions:
            ext_args = ext.args
            for arg in self.args:
                ext_args = [arg.marshal(ext_arg) for ext_arg in ext_args]
            processed_extensions += [ExtensionPragma(ext.name, ext_args)]

        return processed_extensions + self.extensions

    def as_triples(self, context):

        triples = []
        try:
            triples = context.lookup_template(self.template.evaluate(context))
            triples = [marshal(self.args, triple) for triple in triples]
        except KeyError:
            raise TemplateNotFound(self.template.evaluate(
                context), self.template.location)

        if self.name is not None:
            triples = replace_self(triples, self.name)

        old_self = context.current_self
        context.current_self = self.name

        for statement in self.body:
            triples += statement.as_triples(context)

        context.current_self = old_self

        return triples

    def evaluate(self, context):

        name = self.name.evaluate(context)

        triples = self.as_triples(context)
        old_self = context.current_self
        context.current_self = name

        triples = evaluate_triples(triples, context)

        for ext in self.get_extensions(context):
            triples = ext.run(context, triples)

        context.current_self = old_self

        context.add_triples(triples)

        return name

def marshal(arguments, triple):
    (s, p, o) = triple
    for argument in arguments:
        s = argument.marshal(s)
        p = argument.marshal(p)
        o = argument.marshal(o)

    return (s, p, o)


def replace_self(triples, replace_with):
    result = []
    for triple in triples:
        (s, p, o) = triple
        if isinstance(s, Name):
            s = replace_self_in_name(s, replace_with)
        if isinstance(p, Name):
            p = replace_self_in_name(p, replace_with)
        if isinstance(o, Name):
            o = replace_self_in_name(o, replace_with)

        result.append((s, p, o))

    return result

def replace_self_in_name(old_name, _with):
    names = old_name.names
    new_names = []
    for name in names:
        if name == Self() and isinstance(_with, Name):
            new_names += _with.names
        elif name == Self():
            new_names.append(_with)
        else:
            new_names.append(name)

    return Name(*new_names, location=old_name.location)

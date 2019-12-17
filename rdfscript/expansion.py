from rdfscript.core import Argument, Identifier, Name, Node, Self, Uri, Parameter
from rdfscript.pragma import ExtensionPragma
from rdfscript.error import TemplateNotFound

import pdb


class Expansion(Node):
    def __init__(self, identifier, template, args, body, location=None):
        super().__init__(location)
        self.template = template
        self.identifier = Self() if identifier is None else identifier
        self.args = []
        for n in range(0, len(args)):
            arg = args[n]
            if isinstance(arg, Argument):
                self.args.append(Argument(arg.value, n, location))
            else:
                self.args.append(Argument(arg, n, location))

        self.args.append(Argument(self.identifier, -1))

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
        triples = []
        template_uri = self.template.evaluate(context)
        try:
            triples = context.lookup_template(template_uri)
        except KeyError:
            raise TemplateNotFound(template_uri, self.template.location)

        for statement in self.body:
            triples += statement.as_triples(context)

        #if (self.num_expected_arguments(context) -1) != len(self.args):
         #   pdb.set_trace()

        def argument_marshal(triple):
            result = triple
            for argument in self.args:
                result = tuple([argument.marshal(x) for x in result])

            return result

        triples = [argument_marshal(triple) for triple in triples]

        return triples

    def evaluate(self, context):
        identifier = self.identifier.evaluate(context)
        evaluated_args = []
        for arg in self.args:
            evaluated_arg = Argument(arg.value.evaluate(context), arg.position)
            evaluated_args.append(evaluated_arg)

        triples = self.as_triples(context)

        def evaluate_triple(triple):
            return tuple([x.evaluate(context) for x in triple])

        triples = [evaluate_triple(triple) for triple in triples]

        for ext in self.get_extensions(context):
            triples = ext.run(context, triples)

        context.add_triples(triples)

        return identifier

    def num_expected_arguments(self, context):
        template_uri = self.template.evaluate(context)
        try:
            triples = context.lookup_template(template_uri)
        except KeyError:
            raise TemplateNotFound(template_uri, self.template.location)

        def get_top_parameter_in_identifier(identifier):
            top_index = 0
            for part in identifier.parts:
                print(part)
                if isinstance(part, Parameter) and part.position > top_index:
                    top_index = part.position

            return top_index


        num = 0
        for triple in triples:
            try:
                num = max(num, *[get_top_parameter_in_identifier(x) for x in triple])
            except AttributeError:
                pass


        return num
                

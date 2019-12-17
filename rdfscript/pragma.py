from .core import (Node,
                   Name,
                   Assignment)

from .error import FailToImport


class PrefixPragma(Node):

    def __init__(self, prefix, uri, location=None):
        Node.__init__(self, location)

        self._prefix = prefix
        self._uri = uri

    def __eq__(self, other):
        return (isinstance(other, PrefixPragma) and
                self.prefix == other.prefix and
                self.uri == other.uri)

    def __str__(self):
        return format("@prefix %s = %s" % (self.prefix, self.uri))

    def __repr__(self):
        return format("PREFIX DIRECTIVE: (%s, %s)" % (self.prefix, self.uri))

    @property
    def prefix(self):
        return self._prefix

    @property
    def uri(self):
        return self._uri

    def evaluate(self, context):

        uri_to_bind = self.uri.evaluate(context)
        context.bind_prefix(self.prefix, uri_to_bind)
        return uri_to_bind


class DefaultPrefixPragma(Node):

    def __init__(self, prefix, location=None):
        Node.__init__(self, location)

        self._prefix = prefix

    def __eq__(self, other):
        return (isinstance(other, DefaultPrefixPragma) and
                self.prefix == other.prefix)

    def __str__(self):
        return format("@prefix %s" % self.prefix)

    def __repr__(self):
        return format("DEFAULTPREFIX DIRECTIVE: (%s)" % self.prefix)

    @property
    def prefix(self):
        return self._prefix

    def evaluate(self, context):
        context.prefix = self.prefix
        return context.uri_for_prefix(self.prefix)


class ImportPragma(Node):

    def __init__(self, target, location=None):
        Node.__init__(self, location)

        self._target = target

    def __eq__(self, other):
        return (isinstance(other, ImportPragma) and
                self.target == other.target)

    def __str__(self):
        return format("@use %s" % self.target)

    def __repr__(self):
        return format("[IMPORT DIRECTIVE: %s]" % self.target)

    @property
    def target(self):
        return self._target

    def evaluate(self, context):

        uri = self.target.evaluate(context)
        if not context.eval_import(uri):
            raise FailToImport(
                self.target, context.get_current_path(), self.location)

        return self.target


class ExtensionPragma(Node):
    def __init__(self, name, args, location=None):
        super().__init__(location)
        self.name = name
        self.args = args

    def __eq__(self, other):
        return (isinstance(other, ExtensionPragma) and
                self.name == other.name and
                self.args == other.args)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"@extension {self.name}({self.args})"

    def substitute_params(self, parameters):
        for parameter in parameters:
            self.args = [parameter.substitute(arg) for arg in self.args]

    def evaluate(self, context):
        self.args = [arg.evaluate(context) for arg in self.args]
        return self

    def run(self, context, triples):
        self.evaluate(context)
        return context.run_extension_on_triples(self, triples)

    def as_python_object(self, context):

        self.evaluate(context)
        ext_class = context.get_extension(self.name)

        return ext_class(*self.args)

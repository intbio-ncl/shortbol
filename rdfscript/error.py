import pdb

class RDFScriptError(Exception):

    def __init__(self, location):
        if location is not None:
            super().__init__(f"ERROR LINE {location.line} COLUMN {location.col}")
        else:
            super().__init__(f"ERROR")
        self._type = 'RDFScriptError'


class FailToImport(RDFScriptError):

    def __init__(self, target, path, location):
        super().__init__(location)
        self.message += '\n'
        self.message += f"Could not find import '{self.target}'"
        self._type = 'Import Failure Error'
        self._path = path


class RDFScriptSyntax(RDFScriptError):

    def __init__(self, token, location):
        super().__init__(location)
        self.message += '\n'
        self.message += f"Invalid syntax '{self.token}'"
        self._type = 'Invalid Syntax Error'


class UnexpectedType(RDFScriptError):
    def __init__(self, expected, actual, location):
        RDFScriptError.__init__(self, location)
        self._expected = expected
        self._actual = actual
        self._type = 'Unexpected Type Error'

    @property
    def expected(self):
        return self._expected

    @property
    def actual(self):
        return self._actual

    def __str__(self):
        return RDFScriptError.__str__(self) + format("Expected object of type: %s, but found %s.\n\n"
                                                     % (self.expected, self.actual))


class PrefixError(RDFScriptError):

    def __init__(self, prefix, location):
        RDFScriptError.__init__(self, location)
        self._prefix = prefix
        self._type = 'Prefix Error'

    @property
    def prefix(self):
        return self._prefix

    def __str__(self):
        return RDFScriptError.__str__(self) + format("The prefix '%s' is not bound\n\n." % self.prefix)


class TemplateNotFound(RDFScriptError):

    def __init__(self, template, location):
        super().__init__(location)
        self.message += '\n'
        self.message += f"Cound not find template '{template}'"
        self._type = 'Template Not Found Error'


class NoSuchExtension(RDFScriptError):

    def __init__(self, name, location):
        RDFScriptError.__init__(self, location)
        self._name = name
        self._type = 'Extension Not Found Error'

    @property
    def name(self):
        return self._name

    def __str__(self):
        return RDFScriptError.__str__(self) + format("Cannot find extension '%s'.\n\n" % self.name)


class ExtensionFailure(RDFScriptError):

    def __init__(self, message, location):
        RDFScriptError.__init__(self, location)
        if message:
            self._message = message
        else:
            self._message = "An extension failed, but author did not provide message."

        self._type = 'Extension Failed Error'

    def __str__(self):
        return RDFScriptError.__str__(self) + format("%s" % self._message)


class UnknownConstruct(RDFScriptError):

    def __init__(self, construct, location):
        RDFScriptError.__init__(self, location)
        self._construct = construct

    @property
    def construct(self):
        return self._construct

    def __str__(self):
        return RDFScriptError.__str__(self) + format("%s cannot be evaluated.\n\n" % self.construct)


class InternalError(RDFScriptError):

    def __init__(self, core_object, location):
        RDFScriptError.__init__(self, location)
        self._object = core_object
        pdb.set_trace()
        self._type = 'RDFScript Internal Error'

    @property
    def object(self):
        return self._object

    def __str__(self):
        return RDFScriptError.__str__(self) + format("%s caused an internal error.\n\n" % self.object)


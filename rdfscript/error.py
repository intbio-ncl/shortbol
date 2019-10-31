class RDFScriptError(Exception):

    def __init__(self, location):
        self._location = location
        self._type = 'RDFScriptError'

    @property
    def location(self):
        return self._location

    def __str__(self):
        return format("\nERROR: %s on line: %s at position: %s in file: %s\n" % (self._type, self.location.position.line,self.location.col_on_line, self.location.filename))


class FailToImport(RDFScriptError):

    def __init__(self, target, path, location):
        RDFScriptError.__init__(self, location)
        self._target = target
        self._type = 'Import Failure Error'
        self._path = path

    @property
    def target(self):
        return self._target

    def __str__(self):
        return RDFScriptError.__str__(self) + format("Could not find import '%s'\non path %s\n\n"
                                                     % (self.target, self._path))


class RDFScriptSyntax(RDFScriptError):

    def __init__(self, token, location):
        RDFScriptError.__init__(self, location)
        self._token = token
        self._type = 'Invalid Syntax Error'

    @property
    def token(self):
        return self._token

    def __str__(self):
        return RDFScriptError.__str__(self) + format("Did not expect to find '%s'\n\n"
                                                     % self.token)


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
        RDFScriptError.__init__(self, location)
        self._template = template
        self._type = 'Template Not Found Error'

    @property
    def template(self):
        return self._template

    def __str__(self):
        return RDFScriptError.__str__(self) + format("Cannot find template '%s'.\n\n" % self.template)


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
        self._type = 'RDFScript Internal Error'

    @property
    def object(self):
        return self._object

    def __str__(self):
        return RDFScriptError.__str__(self) + format("%s caused an internal error.\n\n" % self.object)

import pdb

class RDFScriptError(Exception):
    def __init__(self, location, msg):
        if location is not None:
            message = f"ERROR LINE {location.line} COLUMN {location.col}:{msg}"
        else:
            message = f"ERROR:{msg}"

        super().__init__(message)
        self._type = 'RDFScriptError'


class FailToImport(RDFScriptError):
    def __init__(self, target, path, location):
        message = '\n'
        message += f"Could not find import '{self.target}'"
        super().__init__(location, message)


class RDFScriptSyntax(RDFScriptError):
    def __init__(self, token, location):
        message = '\n'
        message += f"Invalid syntax '{token}'"
        super().__init__(location, message)


class UnexpectedType(RDFScriptError):
    def __init__(self, expected, actual, location):
        message = '\n'
        message += f"Expected object of type {expected}, but found {actual}"
        super().__init__(location, message)


class PrefixError(RDFScriptError):
    def __init__(self, prefix, location):
        message = '\n'
        message = f"The prefix {prefix} is not bound."
        super().__init__(location, message)


class TemplateNotFound(RDFScriptError):

    def __init__(self, template, location):
        message = '\n'
        message += f"Cound not find template '{template}'"
        super().__init__(location, message)


class NoSuchExtension(RDFScriptError):
    def __init__(self, name, location):
        message = '\n'
        message += f"Cannot find the extension '{name}'"
        super().__init__(location, message)


class ExtensionFailure(RDFScriptError):
    def __init__(self, message, location):
        if message:
            self._message = message
        else:
            self._message = '\n'
            self._message += "An extension failed, but author did not provide message."

        super().__init__(location, self._message)


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


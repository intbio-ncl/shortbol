import pdb

class RDFScriptError(Exception):
    def __init__(self, location, msg):
        self.location = location
        if location is not None:
            message = f"ERROR LINE {location.line} COLUMN {location.col}:{msg} in {location.filename}"
        else:
            message = f"ERROR:{msg}"

        super().__init__(message)
        self._type = 'RDFScriptError'

    def simplified_error_message(self):
        return f'\nERROR: {self._type} on line: {self.location.line} at position: {self.location.col}\n'
    

class FailToImport(RDFScriptError):
    def __init__(self, target, path, location):
        message = '\n'
        message += f"Could not find import '{target}'"
        super().__init__(location, message)


class RDFScriptSyntax(RDFScriptError):
    def __init__(self, token, location):
        self.token = token
        message = '\n'
        message += f"Invalid syntax '{token}'"
        super().__init__(location, message)

    def simplified_error_message(self):
        return f'{RDFScriptError.simplified_error_message(self)}, Did not expect to find: "{self.token.value}"'


class UnexpectedType(RDFScriptError):
    def __init__(self, expected, actual, location):
        self.expected = expected
        self.actual = actual
        message = '\n'
        message += f"Expected object of type {expected}, but found {actual}"
        super().__init__(location, message)

    def simplified_error_message(self):
        return f'{RDFScriptError.simplified_error_message(self)}, Expected object of type: {self.expected}, but found {self.actual}'


class PrefixError(RDFScriptError):
    def __init__(self, prefix, location):
        message = '\n'
        message = f"The prefix {prefix} is not bound."
        super().__init__(location, message)


class TemplateNotFound(RDFScriptError):

    def __init__(self, template, location):
        self.template = template
        message = '\n'
        message += f"Cound not find template '{template}'"
        super().__init__(location, message)

    def simplified_error_message(self):
        return f'{RDFScriptError.simplified_error_message(self)}, Cannot find template: {self.template}'


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

    def simplified_error_message(self):
        return f'{RDFScriptError.simplified_error_message(self)}, {self._message}'


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

    def simplified_error_message(self):
        return f'{RDFScriptError.simplified_error_message(self)}, {self.object} caused an internal error.'
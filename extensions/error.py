class ExtensionError(Exception):

    def __init__(self):
        self._type = 'Extension failure error'

    def __str__(self):
        return format("EXTENSION FAILURE: %s\nDetails:" % self._type)

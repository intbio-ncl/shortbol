import rdflib
import importlib

class ExtensionManager(object):

    def __init__(self, extras=[]):

        self._extensions = {}
        self.add_extra_extension('extensions.cardinality.AtLeastOne',
                                 shortname='AtLeastOne',
                                 base='rdfscript')
        self.add_extra_extension('extensions.sbol.SbolIdentity',
                                 shortname='SbolIdentity')
        self.add_extra_extension('extensions.combinatorialDerivation.CombinatorialDerivation',
                                  shortname="CombinatorialDerivation")
        self.add_extra_extension('extensions.use.Use',
                                  shortname="Use")

        for (name, shortname) in extras:
            self.add_extra_extension(name, shortname=shortname)

    @property
    def extensions(self):
        return self._extensions.keys()

    def add_extra_extension(self, name, shortname=None, base=None):
        if (name in self._extensions or
            (shortname and shortname in self._extensions)):
            raise DuplicateExtension(name)
        else:
            mod, ext = name.rsplit('.', 1)
            mod = importlib.import_module(mod)
            ext = getattr(mod, ext)
            if shortname:
                self._extensions[shortname] = ext
            else:
                self._extensions[name] = ext

    def remove_extension(self, name):
        try:
            del self._extensions[name]
        except KeyError:
            pass

    def get_extension(self, name):
        return self._extensions[name]


class DuplicateExtension(Exception):

    def __init__(self, name):
        self._name = name

    def __str__(self):
        message = (format("ERROR: Extension named %s already exists.\n" % self._name) +
                   format("Choose another name or remove existing extension.\n\n"))
        return message

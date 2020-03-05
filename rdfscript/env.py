import pathlib
import logging

from .core import Uri, Value

from .pragma import ExtensionPragma

from .error import RDFScriptError
from .error import PrefixError

from .parser import Parser

from .importer import Importer

from .extensions import ExtensionManager
from extensions.error import ExtensionError
from extensions.triples import TriplePack
from .rdf_data import RDFData


class Env(object):
    def __init__(self,
                 repl=False,
                 filename=None,
                 serializer=None,
                 paths=[],
                 extensions=[]):

        self._symbol_table = {}
        self._template_table = {}
        self._extension_table = {}
        self._extension_manager = ExtensionManager(extras=extensions)

        self._rdf = RDFData(serializer=serializer)
        self.uri = Uri(self._rdf._g.identifier.toPython())
        self.prefix = None

        self._paths = paths
        if filename:
            paths.append(pathlib.Path(filename).parent)
            self._importer = Importer(paths)
        else:
            self._importer = Importer(paths)

    def __repr__(self):
        return f"{self._rdf.serialise()}"

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, prefix):
        if prefix is not None:
            ns = self._rdf.uri_for_prefix(prefix)

            if not ns:
                raise PrefixError(prefix, None)
            else:
                self._prefix = prefix
                self._uri = ns
        else:
            self._prefix = prefix
            self._uri = Uri(self._rdf._g.identifier.toPython())

        return prefix

    def uri_for_prefix(self, prefix):
        """Return a Uri object for a Prefix object."""
        try:
            return self._rdf.uri_for_prefix(prefix)
        except PrefixError:
            raise PrefixError(prefix, None)

    def prefix_for_uri(self, uri):
        try:
            return self._rdf.prefix_for_uri(uri)
        except PrefixError:
            raise PrefixError(uri, None)

    def add_triples(self, triples):
        """Add a triple of Uri or Value language objects to the RDF graph."""
        for (s, p, o) in triples:
            self._rdf.add(s, p, o)

    def bind_prefix(self, prefix, uri):
        self._rdf.bind_prefix(prefix, uri)
        return prefix

    def assign(self, uri, value):
        self._symbol_table[uri] = value

    def lookup(self, uri):
        return self._symbol_table.get(uri, None)

    def assign_template(self, uri, template):
        self._template_table[uri] = template

    def lookup_template(self, uri):
        triples = self._template_table[uri]
        triples = [triple for triple in triples]
        return triples

    def assign_extensions(self, uri, extensions):
        self._extension_table[uri] = extensions

    def lookup_extensions(self, uri):
        return self._extension_table.get(uri, [])

    def get_extension(self, name):
        return self._extension_manager.get_extension(name)

    def run_extension_on_triples(self, extension, triples):
        #Get type of extension
        extension_class = self.get_extension(extension.name)
        #Creates instance.
        extension_obj = extension_class(*extension.args)    
        #Creates instance of TriplePack which just holds the triples with extra utility.
        pack = TriplePack(triples, self._symbol_table, self._template_table, self._paths)
        return extension_obj.run(pack).triples

    def run_extension_on_graph(self, extension):
        graph_triples = self._rdf.triples
        graph_triples = self.run_extension_on_triples(extension, graph_triples)
        self._rdf.remove_all()
        assert len(self._rdf.triples) == 0

        for triple in graph_triples:
            (s, p, o) = triple
            self._rdf.add(s, p, o)
        return graph_triples

    def interpret(self, forms):
        result = None
        
        for form in forms:
            if isinstance(form, ExtensionPragma):
                form.evaluate(self)
                self.run_extension_on_graph(form)
                result = Value(True)
            else:
                result = form.evaluate(self)
        return result

    def eval_import(self, uri):

        filename = uri.uri
        parser = Parser(filename=filename)

        import_text = self._importer.import_file(filename)
        if not import_text:
            return False
        else:
            old_prefix = self.prefix
            self.interpret(parser.parse(import_text))
            self.prefix = old_prefix
        return True

    def get_current_path(self):

        return [str(p) for p in self._importer.path]

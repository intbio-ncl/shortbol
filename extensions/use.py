import rdflib
import os
from .logic import And
from .error import ExtensionError
from rdfscript.core import Uri, Value,Identifier,Assignment
from rdfscript.pragma import ImportPragma

'''
This Expansion for each template in the given namespace makes and assignment:
user_namespace.template = input_namsespace.template
This enables a user to reference said templates without having to prefix with said namespace.
'''
class Use:
    def __init__(self,namespace):
        self.namespace = namespace.split()[-1]
        self.import_pragma = ImportPragma(Identifier(Uri(self.namespace)))


    def run(self, triplepack, env):
        # Should we make a copy of env and delete it?
        # This way env.evalutate will be called twice (Not sure if its an issue but is not optimal.)
        self.import_pragma.evaluate(env)
        user_prefix = env.uri_for_prefix(env.prefix)
        
        for k in env._template_table.keys():
            if env.uri_for_prefix(self.namespace).uri in k.uri:
                print("Yu")
                name = Identifier(user_prefix,Uri(k.split()[-1]))
                assignment = Assignment(name,k)
                assignment.evaluate(env)
        
        to_evaulate = []
        for k,v in env._symbol_table.items():
            if env.uri_for_prefix(self.namespace).uri in v.uri:
                print("Simp")
                name = Identifier(user_prefix,Uri(k.split()[-1]))
                assignment = Assignment(name,v)
                to_evaulate.append(assignment)
        
        for assingment in to_evaulate:
            assingment.evaluate(env)

        # Triplepack is unchanged but its needed for the late binding that occurs with extensions.
        return triplepack
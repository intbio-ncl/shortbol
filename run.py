import sys
import argparse
import logging
import os
import re
from rdfscript.parser import Parser
from rdfscript.env import Env
from rdfscript.pragma import PrefixPragma,DefaultPrefixPragma,ExtensionPragma
from rdfscript.core import Uri,Identifier,Name
from repl import REPL
from validate_sbol import validate_sbol

default_prefix_name = "shb_ns"
default_prefix = Identifier(Uri("http://shortbol.org/v2#"))

def parse_from_file(filepath,
                    serializer='sbolxml',
                    optpaths=[],
                    out=None,
                    extensions=[],
                    debug_lvl=1, 
                    version="sbol_2",
                    no_validation = None):
    
    if len(optpaths) == 0:
        optpaths.append("templates")

    parser = Parser(filename=filepath, debug_lvl=debug_lvl)

    with open(filepath, 'r', encoding="utf8") as in_file:
        data = in_file.read()


    env = Env(filename=filepath,
              serializer=serializer,
              paths=optpaths,
              extensions=extensions)

    forms = parser.parse(data)
    forms = pre_process(forms,version)
    env.interpret(forms)
    sbol = '<?xml version="1.0" ?>\n' + str(env)

    ret_code = ""
    if not no_validation and serializer == "sbolxml":
        errors = []
        response = validate_sbol(sbol)
        try:
            if response['valid']:
                print('SBOL validator success.')
                ret_code = "SBOL validator success."
            else:
                print("SBOL validator failure.")
                for e in response['errors']:
                    print(e)
                errors = response['errors']
                ret_code =  "SBOL validator failure."
        except TypeError:
            errors = ["Unable to Validate output."]
    else:
        ret_code = "No Validation."
        errors = ["No Validation."]
    if out is None:
        print(sbol)
    else:
        with open(out, 'w') as o:
            o.write(sbol)


    return {ret_code : errors}

def pre_process(forms,version):
    '''
    We want to add a default prefix if one isnt present.
    Also, add the new use extension if not present.
    Also, add the sbol_identity extension
    '''     

    if not any(isinstance(x, PrefixPragma) for x in forms):
        forms.insert(0,PrefixPragma(default_prefix_name,default_prefix))
    
    pos = 0
    if not any(isinstance(x, DefaultPrefixPragma) for x in forms):
        for index,form in enumerate(forms):
            if isinstance(form,PrefixPragma):
                prefix = form.prefix
                pos = index + 1
                break
        forms.insert(pos,DefaultPrefixPragma(prefix))
    else:
        for index,form in enumerate(forms):
            if isinstance(form,DefaultPrefixPragma):
                pos = index + 1

    extensions = [x for x in forms if isinstance(x, ExtensionPragma)]
    use_ns = ExtensionPragma("Use",[Identifier(Name(version))])


    sbol_identity = ExtensionPragma("SbolIdentity",[])
    if use_ns not in extensions:
        print(pos)
        forms.insert(pos + 1,use_ns)
    if version == "sbol_2":
        if sbol_identity not in extensions:
            forms.append(sbol_identity)

    return forms


def rdf_repl(serializer='nt',
             out=None,
             optpaths=[],
             extensions=[],
             debug_lvl=1):

    print("Building parser with yacc...")
    print("Parser build success...")
    print("Lexer build success... Enjoy your RDF...")
    print("#"*40)

    repl = REPL(serializer=serializer,
                out=out,
                optpaths=optpaths,
                optextensions=extensions,
                debug_lvl=debug_lvl)

    repl.start()

def produce_tables(version = "sbol_2", lib_paths = None):
    '''
    Method that is independant from the rdf/xml production, simply runs the parsing and evaluation 
    process on the templates to produce the symbols and template tables.
    This process is just the parse_from file method and returns the tables.
    '''
    if lib_paths is None:
        optpaths = [os.path.join(os.getcwd(),"templates")]
    else:
        optpaths = [lib_paths]
    to_run_fn = os.path.join(optpaths[0],"temp.shb")
    f= open(to_run_fn,"a")
    f.write("use <" + version + ">")
    f.close()

    parser = Parser(filename=to_run_fn, debug_lvl=1)

    with open(to_run_fn, 'r') as in_file:
        data = in_file.read()

    env = Env(filename=to_run_fn,
              serializer="sbolxml",
              paths=optpaths)

    forms = parser.parse(data)
    forms = pre_process(forms,version)
    env.interpret(forms)
    prefixes = [prefix for prefix in env._rdf._g.namespaces()]
    os.remove(to_run_fn)
    return env._symbol_table, env._template_table, prefixes


def rdfscript_args():

    parser = argparse.ArgumentParser(description="RDFScript interpreter and REPL.")

    parser.add_argument('-s', '--serializer', default="sbolxml",
                        choices=['rdfxml', 'n3', 'turtle', 'sbolxml', 'nt'],
                        help="The format into which the graph is serialised")
    parser.add_argument('-p', '--path',
                        help="Additions to the path in which to search for imports",
                        nargs='*',
                        default=[])
    parser.add_argument('filename', default=None, nargs='?',
                        help="File to parse as RDFScript")

    parser.add_argument('-o', '--output', help="The name of the output file", default="shortbol_output.rdf")
    parser.add_argument('-nv', '--no_validation', help="Stops the output from being sent via HTTP to online validator.", default=None, action='store_true')
    parser.add_argument('-no', '--no_output', help="Stops writing output to file, instead prints to console.", default=None, action='store_true')
    parser.add_argument('-e', '--extensions', action='append', nargs=2, default=[])
    parser.add_argument('-v', '--version', help="Define which SBOL version to run (3 by default)", choices=["sbol_2","sbol_3"] , default="sbol_2")

    parser.add_argument('-d', '--debug-lvl', default=1,
                        choices=[0, 1, 2],
                        help="Controls the amount of debug information generated. 0 is low/none.")

    return  parser.parse_args()

if __name__ == "__main__":

    logging.basicConfig(format='\n%(message)s\n', level=logging.DEBUG)
    args = rdfscript_args()
    extensions = [(ext[0], ext[1]) for ext in args.extensions]
    out = None if args.no_output else args.output  
    if args.filename is not None:
        parse_from_file(args.filename,
                        serializer=args.serializer,
                        out=out,
                        optpaths=args.path,
                        extensions=extensions,
                        debug_lvl=args.debug_lvl,
                        version=args.version,
                        no_validation = args.no_validation)
    else:
        rdf_repl(serializer=args.serializer,
                 out=args.output,
                 optpaths=args.path,
                 extensions=extensions,
                 debug_lvl=args.debug_lvl)

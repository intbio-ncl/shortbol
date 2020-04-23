import sys
import argparse
import logging
import os
import re
from rdfscript.parser import Parser
from rdfscript.env import Env
from repl import REPL
from validate_sbol import validate_sbol


#SBOL Namespace
f_prefix = "@prefix"
sbol_compliant_extension = "@extension SbolIdentity()"

def hacky_conversion(filepath, temp_file, template_dir,version):
    # Check if sbol namespace present. (use <sbol>)
    sbol_namespace = "use <" + version + ">"
    with open(filepath, 'r') as original: data = original.readlines()
    
    split_text = data
    if not sbol_namespace in split_text:
        split_text.insert(0,sbol_namespace + "\n")

    # check if named prefix only is present (@prefix name)
    sbol_import = f_prefix +  " " + version + "\n"
    if not any(sbol_import in x for x in split_text):
        split_text.insert(1,sbol_import)


    # Check if sbol compliant extension is present @extension SbolIdentity()
    if not sbol_compliant_extension in split_text and version == "sbol_2":
        split_text.append(sbol_compliant_extension)
        
    with open(temp_file, 'w') as modified:
        for line in split_text:
            modified.write(line)
            modified.write("\n")

    return temp_file


def parse_from_file(filepath,
                    serializer='sbolxml',
                    optpaths=[],
                    out=None,
                    extensions=[],
                    debug_lvl=1, 
                    version="sbol_2",
                    no_validation = None,
                    no_hack = None):
    
    if len(optpaths) == 0:
        optpaths.append("templates")
    template_dir = os.path.join(optpaths[0], str(version))
    if not no_hack:
        temp_file = os.path.join(os.path.dirname(filepath), "temporary_runner.shb")
        if os.path.isfile(temp_file):
            os.remove(temp_file)
        to_run_fn = hacky_conversion(filepath,temp_file,template_dir,str(version))
    else:
        to_run_fn = filepath

    parser = Parser(filename=to_run_fn, debug_lvl=debug_lvl)

    with open(to_run_fn, 'r') as in_file:
        data = in_file.read()


    env = Env(filename=to_run_fn,
              serializer=serializer,
              paths=optpaths,
              extensions=extensions)
    if not no_hack:
        if temp_file :
            os.remove(temp_file)
    forms = parser.parse(data)
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
    parser.add_argument('-nh', '--no_hack', help="Stops the hack from modiying the file.", default=None, action='store_true')
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
                        no_validation = args.no_validation,
                        no_hack = args.no_hack)
    else:
        rdf_repl(serializer=args.serializer,
                 out=args.output,
                 optpaths=args.path,
                 extensions=extensions,
                 debug_lvl=args.debug_lvl)

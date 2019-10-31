import sys
import argparse
import logging
import os
from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.env import Env
from repl import REPL



def hacky_conversion(filepath):
    '''
    This is a hack method that modifies the input if it is not currrently shortbol namespace valid
    '''
    temp_file = os.path.join(os.path.dirname(filepath), "temporary_runner.rdfsh")
    if os.path.isfile(temp_file):
        os.remove(temp_file)


    
    #SBOL Namespace
    sbol_namespace = "use <sbol>"
    f_prefix = "@prefix sbol"
    f_equals = " = "
    default_prefix = "<http://sbols.org/>"
    s_prefix = "@prefix "
    sbol_compliant_extension = "@extension SbolIdentity()"
    is_a_template = "is a"

    with open(filepath, 'r') as original: data = original.read()
    split_text = data.split("\n")
    for index,line in enumerate(split_text):
        print(index,line)

    # Check if sbol namespace present.
    if not sbol_namespace in split_text:
        split_text.insert(0,sbol_namespace + "\n")

    # Check if prefix are present.
    if len([s for s in split_text if s_prefix in s]) == 0:
        split_text.insert(1,f_prefix + f_equals +  default_prefix)
        split_text.insert(2,f_prefix)
    # check if named prefix only is present
    if len([s for s in split_text if s_prefix in s]) == 1:
        for index,line in enumerate(split_text):
            if s_prefix in line:
                split_text.insert(index + 1,s_prefix + line.split(" ")[1])
                break
    # Check if sbol compliant extension is present
    if not sbol_compliant_extension in split_text:
        split_text.append(sbol_compliant_extension)




    shortbol_templates_dir = os.path.join("templates","sbol")
    for filename in os.listdir(shortbol_templates_dir):
        if filename.endswith(".rdfsh"): 
            print(os.path.join(shortbol_templates_dir, filename))
            continue
        else:
            continue
    templates = [s for s in split_text if is_a_template in s]
    
    for template in templates:
        parts = template.split(" ")
        print(parts)
        # Get all possible templates

    

        
    # Create a list of types from Shortbol2 libs

    with open(temp_file, 'w') as modified:
        for line in split_text:
            modified.write(line)
            modified.write("\n")



    return temp_file

def parse_from_file(filepath,
                    serializer='nt',
                    optpaths=[],
                    out=None,
                    extensions=[],
                    debug_lvl=1):
    
    optpaths.append("templates")

    to_run_fn = hacky_conversion(filepath)
    print(extensions)
    return

    parser = RDFScriptParser(filename=filepath, debug_lvl=debug_lvl)

    with open(filepath, 'r') as in_file:
        data = in_file.read()

    env = Env(filename=filepath,
              serializer=serializer,
              paths=optpaths,
              extensions=extensions)

    forms = parser.parse(data)
    env.interpret(forms)
    if not out:
        print(env)
    else:
        with open(out, 'w') as o:
            o.write(str(env))
            print("Valid.")

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

def rdfscript_args():

    parser = argparse.ArgumentParser(description="RDFScript interpreter and REPL.")

    parser.add_argument('-s', '--serializer', default='nt',
                        choices=['rdfxml', 'n3', 'turtle', 'sbolxml', 'nt'],
                        help="The format into which the graph is serialised")
    parser.add_argument('-p', '--path',
                        help="Additions to the path in which to search for imports",
                        nargs='*',
                        default=[])
    parser.add_argument('filename', default=None, nargs='?',
                        help="File to parse as RDFScript")

    parser.add_argument('-o', '--output', help="The name of the output file", default=None)
    parser.add_argument('--version', action='version', version='%(prog)s 0.0alpha')
    parser.add_argument('-e', '--extensions', action='append', nargs=2, default=[])

    parser.add_argument('-d', '--debug-lvl', default=1,
                        choices=[0, 1, 2],
                        help="Controls the amount of debug information generated. 0 is low/none.")

    return  parser.parse_args()

if __name__ == "__main__":

    logging.basicConfig(format='\n%(message)s\n', level=logging.DEBUG)
    args = rdfscript_args()
    extensions = [(ext[0], ext[1]) for ext in args.extensions]

    if args.filename is not None:
        parse_from_file(args.filename,
                        serializer=args.serializer,
                        out=args.output,
                        optpaths=args.path,
                        extensions=extensions,
                        debug_lvl=args.debug_lvl)
    else:
        rdf_repl(serializer=args.serializer,
                 out=args.output,
                 optpaths=args.path,
                 extensions=extensions,
                 debug_lvl=args.debug_lvl)

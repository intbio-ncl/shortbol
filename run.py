import sys
import argparse
import logging
import os
from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.env import Env
from repl import REPL


def parse_from_file(filepath,
                    serializer='nt',
                    optpaths=[],
                    out=None,
                    extensions=[],
                    debug_lvl=1):
    
    optpaths.append("templates")
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

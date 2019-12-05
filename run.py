import sys
import argparse
import logging
import os
import re
from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.env import Env
from repl import REPL
from validate_sbol import validate_sbol



def hacky_conversion(filepath,template_dir):
    '''
    This is a hack method that modifies the input if it is not currrently shortbol namespace valid
    '''
    temp_file = os.path.join(os.path.dirname(filepath), "temporary_runner.rdfsh")
    if os.path.isfile(temp_file):
        os.remove(temp_file)

    #SBOL Namespace
    sbol_namespace = "use <sbol>"
    f_prefix = "@prefix sbol_prefix"
    f_equals = " = "
    default_prefix = "<http://sbol_prefix.org/>"
    s_prefix = "@prefix "
    sbol_compliant_extension = "@extension SbolIdentity()"
    is_a_template = "is a"
    sbol_dot = "sbol."
    

    
    with open(filepath, 'r') as original: data = original.read()
    split_text = data.split("\n")

    # Check if sbol namespace present. (use <sbol>)
    if not sbol_namespace in split_text:
        split_text.insert(0,sbol_namespace + "\n")

    # Check if prefix are present. (@prefix name = <> )
    if len([s for s in split_text if s_prefix in s]) == 0:
        split_text.insert(1,f_prefix + f_equals +  default_prefix)
        split_text.insert(2,f_prefix)
    # check if named prefix only is present (@prefix name)
    if len([s for s in split_text if s_prefix in s]) == 1:
        for index,line in enumerate(split_text):
            if s_prefix in line:
                split_text.insert(index + 1,s_prefix + line.split(" ")[1])
                break
    # Check if sbol compliant extension is present @extension SbolIdentity()
    if not sbol_compliant_extension in split_text:
        split_text.append(sbol_compliant_extension)

    

    shortbol_template_table = set()
    shortbol_identifier_table = set()

    sbol_dir = os.path.join(template_dir,"sbol")
    for filename in os.listdir(sbol_dir):
        if filename.endswith(".rdfsh"): 
            template = open(os.path.join(sbol_dir, filename), "r")
            for line in template:
                x = re.search(".+[(].*[)]", line)
                if x is not None:
                    shortbol_template_table.add(x.group(0).replace(" ","").split("(")[0])
                else:
                    x = re.search(".+[<].*[>]",line)
                    if x is not None:
                        shortbol_identifier_table.add(x.group(0).replace(" ","").split("=")[0])
            template.close()


    for index,line in enumerate(split_text):
        if line and line[0].lstrip() == "#" :
            continue 
        if is_a_template in line :
            name = line.split(is_a_template)[0]
            try:
                params = "(" + line.split("(")[1]
            except IndexError:
                raise NameError("Template: " + name + " on line: " + str(index - 1) + " is missing brackets.") 
            
            parts = line.split(is_a_template)[-1].split("(")[0]
            parts = parts.replace(" ", "")
            parts = parts.split(".")
            # When sbol. is not present
            if len(parts) == 1 :
                if parts[0] in shortbol_template_table:
                    #SBOL. is not present and template is in libary
                    split_text[index] = name + is_a_template + " " + sbol_dot + parts[0]
                    
                else:
                    raise NameError("Template: " + parts[0] + " on line: " + str(index - 1) + " is not defined in the Shortbol Libaries.") 
                    #SBOL. is not present but template NOT in libary
            elif len(parts) == 2:
                if parts[1] in shortbol_template_table:
                    #SBOL. is  present and template is in libary
                    continue
                else:
                    raise NameError("Template: " + parts[0] + " on line: " + str(index - 1) + " is not defined in the Shortbol Libaries.") 
                    #SBOL. is  present but template NOT in libary
            else:
                exit(0)

            split_params = params.replace("(","").replace(")","").split(",")
            param_string = ""
            if len(split_params) == 0:
                param_string = "()"
            elif len(split_params) == 1 :
                if sbol_dot not in split_params[0] and split_params[0] in shortbol_identifier_table:
                    param_string = sbol_dot + split_params[0]
                else:
                    param_string = split_params[0]
            else:
                for param_index, param in enumerate(split_params):
                    split_params[param_index] = split_params[param_index].replace(" ", "")
                    if sbol_dot not in split_params[param_index] and split_params[param_index] in shortbol_identifier_table:
                        param_string = param_string + sbol_dot + split_params[param_index]
                        if param_index != len(split_params) - 1 :
                            param_string = param_string + ","
                    else:
                        param_string = param_string + split_params[param_index]
                        if param_index != len(split_params) - 1 :
                            param_string = param_string + ","

            split_text[index] = split_text[index] + "(" + param_string + ")"

            # When extension is present, cueco each statement inside and add sbol where needed.
            if split_text[index + 1] == "(" :
                curr_line_num = index + 2
                
                while split_text[curr_line_num] != ")":
                    if "=" not in split_text[curr_line_num] or split_text[curr_line_num].lstrip()[0] == "#":
                        curr_line_num = curr_line_num + 1
                        continue
                    if "displayId" in split_text[curr_line_num]:
                        print("Warn for Template: " + name + ", displayId property should not be overwritten, " + name +  "will be used.") 
                        split_text[curr_line_num] = ""
                        curr_line_num = curr_line_num + 1
                        continue
                    if "persistentIdentity" in split_text[curr_line_num]:
                        print("Warn for Template: " + name + ", persistentIdentity property should NEVER be overwritten.") 
                        split_text[curr_line_num] = ""
                        curr_line_num = curr_line_num + 1
                        continue
                    
                    sections = split_text[curr_line_num].split("=")
                    lhs = sections[0]
                    rhs = sections[-1]
                    if '"' not in rhs:
                        rhs = rhs.replace(" ", "")
                    if sbol_dot not in lhs:
                        lhs = lhs.lstrip()
                        lhs = lhs.replace(" ", "")
                        lhs = "    " + sbol_dot + lhs
                    if sbol_dot not in rhs:
                        if rhs in shortbol_identifier_table:
                            rhs = sbol_dot + rhs
                                        
                    #Re assemble line
                    split_text[curr_line_num] = lhs + " = " + rhs 
                    curr_line_num = curr_line_num + 1
            
  

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
                    debug_lvl=1,
                    no_validation = None):
    
    if len(optpaths) == 0:
        optpaths.append("templates")
    template_dir = optpaths[0]

    to_run_fn = hacky_conversion(filepath,template_dir)

    parser = RDFScriptParser(filename=to_run_fn, debug_lvl=debug_lvl)

    with open(to_run_fn, 'r') as in_file:
        data = in_file.read()

    env = Env(filename=to_run_fn,
              serializer=serializer,
              paths=optpaths,
              extensions=extensions)

    forms = parser.parse(data)
    env.interpret(forms)
    if not out:
        print(env)
    else:
        with open(out, 'w') as o:
            sbol = str(env)
        
            ret_code = ""
            if not no_validation:
                errors = []
                response = validate_sbol(sbol)
                if response['valid']:
                    print('Valid.')
                    ret_code = "Valid."
                else:
                    for e in response['errors']:
                        print(e)
                    errors = response['errors']
                    ret_code =  "Invalid."
            else:
                ret_code = "No Validation."
                errors = ["No Validation."]

            xml_preamble = '<?xml version="1.0" ?>\n'
            o.write(xml_preamble)
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


def produce_tables(lib_paths):
    '''
    Method that is independant from the rdf/xml production, simply runs the parsing and evaluation 
    process on the templates to produce the symbols and template tables.
    This process is just the parse_from file method and returns the tables.
    '''
    optpaths = lib_paths
    to_run_fn = os.path.join(lib_paths,"temp.rdfsh")
    f= open(to_run_fn,"a")
    f.write("use <sbol>")
    f.close()

    parser = RDFScriptParser(filename=to_run_fn, debug_lvl=1)

    with open(to_run_fn, 'r') as in_file:
        data = in_file.read()

    env = Env(filename=to_run_fn,
              serializer="sbolxml",
              paths=optpaths)

    forms = parser.parse(data)
    env.interpret(forms)
    os.remove(to_run_fn)
    return env._symbol_table, env._template_table

   

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
    parser.add_argument('-nv', '--no_validation', help="Stops the output from being sent via HTTP to online validator.", default=None, action='store_true')
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
                        debug_lvl=args.debug_lvl,
                        no_validation = args.no_validation)
    else:
        rdf_repl(serializer=args.serializer,
                 out=args.output,
                 optpaths=args.path,
                 extensions=extensions,
                 debug_lvl=args.debug_lvl)

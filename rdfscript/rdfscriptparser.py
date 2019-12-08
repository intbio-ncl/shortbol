import ply.yacc as yacc
import ply.lex as lex
import logging
from . import reader

from .reader import tokens

from .core import (Uri,Name,Value,Self,Assignment,Variable)

from .pragma import (PrefixPragma,
                     DefaultPrefixPragma,
                     ImportPragma,
                     ExtensionPragma)

from .template import Template, Property
from .expansion import Expansion

from .error import RDFScriptSyntax


# script level
def p_forms(p):
    '''forms : form forms'''
    p[0] = [p[1]] + p[2]


def p_empty_forms(p):
    '''forms : empty'''
    p[0] = []


def p_form_types(p):
    '''form : assignment
            | extension
            | template
            | expr'''
    p[0] = p[1]


# assignment
def p_assignment(p):
    '''assignment : name '=' expr'''
    p[0] = Assignment(p[1], p[3], location(p))


# pragma
def p_pragma_prefix(p):
    '''pragma : PREFIX SYMBOL '=' expr'''
    l = location(p)
    p[0] = PrefixPragma(p[2], p[4], l)


def p_defaultprefix_pragma(p):
    '''pragma : PREFIX SYMBOL'''
    l = location(p)
    p[0] = DefaultPrefixPragma(p[2], l)


def p_pragma_import(p):
    '''pragma : USE name'''
    p[0] = ImportPragma(p[2], location(p))


def p_extension_no_args(p):
    '''extension : EXTENSION SYMBOL'''
    p[0] = ExtensionPragma(p[2], [], location(p))


def p_extension_args(p):
    '''extension : EXTENSION SYMBOL '(' exprlist ')' '''
    p[0] = ExtensionPragma(p[2], p[4], location(p))

## expansions and templates

def p_template(p):
    '''template : name '(' exprlist ')' indentedinstancebody'''
    p[0] = Template(p[1], p[3], p[5], location=location(p))

def p_expansion(p):
    '''expansion : name ISA name '(' exprlist ')' indentedinstancebody'''
    p[0] = Expansion(p[1], p[3], p[5], p[7], location(p))

def p_anon_expansion(p):
    '''anon_expansion : name '(' exprlist ')' indentedinstancebody'''
    p[0] = Expansion(None, p[1], p[3], p[5], location(p))

# def p_triple(p):
#     '''triple : name name expr'''
#     p[0] = TripleObject(p[1], p[2], p[3], location(p))


def p_expr(p):
    '''expr : name
            | pragma
            | literal
            | expansion'''
    p[0] = p[1]


def p_indentedinstancebody(p):
    '''indentedinstancebody : '(' instancebody ')' '''
    p[0] = p[2]


def p_empty_indentedinstancebody(p):
    '''indentedinstancebody : empty'''
    p[0] = []


def p_instancebody(p):
    '''instancebody : bodystatements'''
    p[0] = p[1]

# bodies


def p_bodystatements(p):
    '''bodystatements : bodystatement bodystatements'''
    p[0] = [p[1]] + p[2]


def p_empty_bodystatements(p):
    '''bodystatements : empty'''
    p[0] = []


def p_bodystatement(p):
    '''bodystatement : property
                     | expansion
                     | anon_expansion
                     | extension'''
    p[0] = p[1]


def p_property(p):
    '''property : name '=' expr'''
#                | name '=' expansion'''
    p[0] = Property(p[1], p[3], location=location(p))

# lists


def p_exprlist(p):
    '''exprlist : emptylist
                | notemptyexprlist'''
    p[0] = p[1]


def p_not_empty_exprlist_1(p):
    '''notemptyexprlist : expr'''
    p[0] = [p[1]]


def p_not_empty_exprlist_n(p):
    '''notemptyexprlist : expr ',' notemptyexprlist'''
    p[0] = [p[1]] + p[3]


def p_empty(p):
    '''empty :'''
    pass


def p_emptylist(p):
    '''emptylist : empty'''
    p[0] = []

# names


def p_dotted_name(p):
    '''name : dotted_list'''
    l = location(p)
    p[0] = Variable(*p[1], location=l)


def p_dotted_list_1(p):
    '''dotted_list : identifier'''
    p[0] = [p[1]]


def p_dotted_list_n(p):
    '''dotted_list : identifier '.' dotted_list'''
    p[0] = [p[1]] + p[3]


def p_identifier(p):
    '''identifier : SYMBOL
                  | uri
                  | self'''
    p[0] = p[1]


def p_self(p):
    '''self : SELF'''
    p[0] = Self(location(p))


def p_uri(p):
    '''uri : URI'''
    p[0] = Uri(p[1], location=location(p))

# literal objects


def p_literal(p):
    '''literal : INTEGER
               | STRING
               | DOUBLE'''
    p[0] = Value(p[1], location(p))


def p_literal_boolean(p):
    '''literal : BOOLEAN'''
    if p[1] == 'true':
        p[0] = Value(True, location(p))
    else:
        p[0] = Value(False, location(p))

# SYNTAX ERROR


def p_error(p):
    if not p:
        pass
    else:
        location = Location(p.lineno, p.lexpos, p.lexer.filename)
        raise RDFScriptSyntax(p, location)


def location(p):
    return Location(p.lineno(0), p.lexpos(0), p.parser.filename)


def make_parser(filename=None):
    parser = yacc.yacc()
    parser.filename = filename
    return parser


def make_lexer(filename=None):
    lexer = lex.lex(module=reader)
    lexer.open_brackets = 0
    lexer.filename = filename
    return lexer


class RDFScriptParser:

    def __init__(self, debug_lvl=0, filename=None):

        self.scanner = make_lexer(filename)
        self.debug = debug_lvl != 0
        self.dbg_logger = None
        if debug_lvl == 2:
            self.dbg_logger = logging.getLogger()

        self.parser = make_parser(filename)

    def parse(self, script):

        return self.parser.parse(script,
                                 lexer=self.scanner,
                                 tracking=True,
                                 debug=self.dbg_logger)


class Location:

    def __init__(self, line, column, filename=None):
        self.line = line
        self.col = column

        if not filename:
            self.filename = "REPL"
        else:
            self.filename = filename

    def __repr__(self):
        return format("%s in '%s'" % (self.position, self.filename))

    @property
    def col_on_line(self):
        with open(self.filename) as infile:
            characters = 0
            for lineno, line in enumerate(infile, 1):
                if lineno == self.line:
                    return self.col - characters
                characters += sum(len(word) for word in line)
            return self.col

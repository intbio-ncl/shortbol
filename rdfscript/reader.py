import ply.lex as leex
import sys

tokens = (
     "SYMBOL",
     "BOOLEAN",
     "STRING",
     "INTEGER",
     "DOUBLE",
     "URI",
     "SELF",
     "ISA",
     "FROM",
     "PREFIX",
     "EXTENSION",
     "USE")

t_ignore = '\t'
literals = ['=',
            '{', '}',
            '(', ')',
            '.',
            '[', ']',
            ':',
            '*',
            ',']

reserved_words = {
     'true'           : 'BOOLEAN',
     'false'          : 'BOOLEAN',
     '@prefix'        : 'PREFIX',
     '@use'           : 'USE',
     'use'            : 'USE',
     '@extension'     : 'EXTENSION',
     'self'           : 'SELF',
     'from'           : 'FROM'
    }

def t_eof(t):
     if not t.lexer.open_brackets == 0:
          if sys.version_info >= (3, 0):
               more = input('... ')
          else:
               more = raw_input('... ')

          if more:
               t.lexer.input(more)
               return t.lexer.token()
          
     return None

def t_lbracket(t):
     r'\('
     t.lexer.open_brackets += 1
     t.type = '('
     return t

def t_rbracket(t):
     r'\)'
     t.lexer.open_brackets -= 1
     t.type = ')'
     return t

def t_ISA(t):
     r'is\s+a'
     t.type = 'ISA'
     t.value = 'is a'
     return t

#Multiline strings can be defined by either triple quotes or () around all quotes with string ending on each line |\(((?:")[\S\s]*?(?:"))*\)
def t_STRING(t):
    r'(?:").*?(?:")' #\"(\\.|[^"\\])*\"
    t.value = t.value[1:-1]
    return t

def t_URI(t):
    r'<[^<>]*>'
    t.value = t.value[1:-1]
    return t

def t_COMMENT(t):
    r'[ ]*\#[^\n]*'
    pass

def t_SYMBOL(t):
     r'[^\(\)}{=."\'\s\[\],0-9\-]+[^()}{=."\'\s\[\],]*'
     t.type = reserved_words.get(t.value, 'SYMBOL')
     return t

def t_DOUBLE(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INTEGER(t):
    r'[-]?\d+'
    t.value = int(t.value)
    return t

def t_newline(t):
     r'[ ]*\n+'
     t.lexer.lineno += len(t.value)

def t_WS(t):
     r'\s'
     pass

def t_error(t):
    print("Could not scan token '%s' at line %d" % (t.value[0], t.lexer.lineno))
    t.lexer.skip(1)

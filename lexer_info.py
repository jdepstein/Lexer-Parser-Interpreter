import re
from collections import namedtuple
# All of Tokens/Identifiers
Token = namedtuple('Token', 'name')
PLUS = Token("PLUS")
MINUS = Token("MINUS")
TIMES = Token("TIMES")
DIVISION = Token("DIVISION")
IDENT = Token("IDENT")
LPAREN = Token("LPAREN")
RPAREN = Token("RPAREN")
COMMA = Token("COMMA")
SEMI = Token("SEMI")
LCURLY = Token("LCURLY")
RCURLY = Token("RCURLY")
QUOTE = Token("QUOTE")
INTLIT = Token("INTLIT")
REAL = Token("REAL")
EQULITY = Token("EQULITY")
DECLERATION = Token("DECLERATION")
NOTEQUAL = Token("NOTEQUAL")
GREATERTHAN = Token("GREATERTHAN")
LESSTHAN = Token("LESSTHAN")
DOUBGREATERTHAN = Token("DOUBGREATERTHAN")
DOUBLESSTHAN = Token("DOUBLESSTHAN")
OR = Token("OR")
AND = Token("AND")
LET = Token("LET")
GET = Token("GET")
RSB = Token("RSB")
LSB = Token("LSB")
NOT = Token("NOT")
MOD = Token("MOD")
ERROR = Token("ERROR")
EOF = Token("EOF")
String_Lit = Token("STRING_LIT")
IF = Token("if")
WHILE = Token("while")
PRINT = Token("print")
TRUE = Token("True")
FALSE = Token("False")
RETURN = Token("return")
ELSE = Token("else")
FOR = Token("for")
INT = Token("INT")
FLOAT = Token("FLOAT")
BOOLEAN = Token("BOOLEAN")
TF = Token("BOOL")


# Dictionary match Tokens and their Name
td = {
            ')':  RPAREN,
            '(':  LPAREN,
            '+':  PLUS,
            '*':  TIMES,
            ',':  COMMA,
            ';':  SEMI,
            '{':  LCURLY,
            '}':  RCURLY,
            '=':  DECLERATION,
            '==': EQULITY,
            '!=': NOTEQUAL,
            '>':  GREATERTHAN,
            '<':  LESSTHAN,
            '>>': DOUBGREATERTHAN,
            '<<': DOUBLESSTHAN,
            '||': OR,
            '&&': AND,
            '[':  RSB,
            ']':  LSB,
            '>=': GET,
            '<=': LET,
            '/':  DIVISION,
            '!':  NOT,
            '%':  MOD,
            '-':  MINUS,
            'if':     IF,
            'for':    FOR,
            'while':  WHILE,
            'and':    AND,
            'True':   TRUE,
            'False':  FALSE,
            'or':     OR,
            'else':   ELSE,
            'return': RETURN,
            'print':  PRINT,
            'int': INT,
            'float': FLOAT,
            'bool': BOOLEAN,
            'true': TF,
            'false': TF}

# String pattern
string_comment = re.compile(
    """
     ("[\sA-Za-z0-9+-{}';:><?!@#$%^&*()=|.,/]+") |
     //[\s\S]*
    """, re.VERBOSE)

# General pattern
split_patt = re.compile(
    """                  # Split on ...
      ("[\sA-Za-z0-9+-{}';:><?!@#$%^&*()=|.,/]+") |
      \s(-) |           #  negative/Minus Sign
      (-)   |
      \s(\+) |           #  positive/Plus Sign
      (\+)   |  
      (/)    |
      \s     |           #  whitespace
      (\()   |           #  left paren
      (\))   |           #  right paren
      (==)   |           #  equality
      (=)    |           #  assignment
      (\*)   |           #  times
      (!)    |           #  Not
      (,)    |           #  comma
      (;)    |           #  Simi
      ({)    |           #  left curly
      (\})   |           #  right curly
      (\[)   |  #  Right square
      (\])   |  #  left square
      (>=) |  #  Greater Than or Equal
      (<=) |  #  Less Than or Equal 
      (!=) |  #  Not Equal too
      (<<) |  #  Double Less Than
      (>>)    #  Double Greater Than

     
   """,
    re.VERBOSE)


# Pattern for Words
ident_patt = re.compile('^[a-zA-Z_]\w*$', re.ASCII)

# Pattern for Stirngs
string_patt = re.compile('("[\s\S]+")', re.ASCII)

# Pattern for int numbers
intlit_patt = re.compile("""
                            (^\d+$)
                           """, re.VERBOSE)

# Patter for real numbers
real_patt = re.compile("""
                       (^\d*\.\d+ [eE] \d+$)               |
                       (^\d*\.\d+ [eE]) ([+-] \d+$)        |
                       (^\d+ [eE] \d+$)                    |
                       (^\d+ [eE]) ([+-] \d+$)             |
                       (^\d* \. \d+$)
                        """, re.VERBOSE)


"""intlit_patt = re.compile( 


             (( (\d+)_\d*)+ \.((\d+)_\d*)+) (\d)$    |  # Undscore Both Sides
             (( (\d+)_\d*)+ \. (\d+))       (\d)$    |  # Underscore Number with decimals 
             (\d* \.((\d+)_\d*)+)           (\d)$    |  # Number Decimals with Underscores
             ((\d+_\d*)+)                   (\d)$    |  # Numbers with Underscore's
             (\d* \.\d+)                    (\d)$    |  # Decimal Number
             (\d+)                          (\d)$       # Regular Number
        ,
           re.VERBOSE)"""

"""re.compile(  
             (( (\d+)_\d*)+ \.((\d+)_\d*)+) ([eE]) (([+-] ( ((\d+_\d*)*) ? (\d+$)))   ? \d+$)|  
             (( (\d+)_\d*)+ \. (\d+))       ([eE]) (([+-] ( ((\d+_\d*)*) ? (\d+$)))   ? \d+$)| 
             (\d* \.((\d+)_\d*)+)           ([eE]) (([+-] ( ((\d+_\d*)*) ? (\d+$)))   ? \d+$)|  
             ((\d+_\d*)+)                   ([eE]) (([+-] ( ((\d+_\d*)*) ? (\d+$)))   ? \d+$)|  
             (\d* \.\d+)                    ([eE]) (([+-] ( ((\d+_\d*)*) ? (\d+$)))   ? \d+$)| 
             (\d+)                          ([eE]) ([+-]  ((\d+_\d*)*)  ?  (\d+$))           |
             (\d+)                          ([eE])                                      \d+$          
            ,
            re.VERBOSE)"""

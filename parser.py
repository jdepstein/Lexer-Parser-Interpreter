import re
import sys
from lexer import Lexer
from ast import *
from ast import SLUCSyntaxError as slusyn
from ast import SLUCTypeError as slutype
"""
 Program → { FunctionDef }
 FunctionDef → Type id ( Params ) { Declarations Statements }
 Params → Type id { , Type id } | ε
 Declarations → { Declaration }
 Declaration → Type Identifier ;
 Type → int | bool | float
 Statements → { Statement }
 Statement → ; | Block | Assignment | IfStatement | WhileStatement
 | PrintStmt | ReturnStmt
 ReturnStmt → return Expression ;
 Block → { Statements }
 Assignment → id = Expression ;
 IfStatement → if ( Expression ) Statement [ else Statement ]
 WhileStatement → while ( Expression ) Statement
 PrintStmt → print( PrintArg { , PrintArg })
 PrintArg → Expression | stringlit
 Expression → Conjunction { || Conjunction }
 Conjunction → Equality { && Equality }
 Equality → Relation [ EquOp Relation ]
 Relation → Addition [ RelOp Addition ]
 Addition → Term { AddOp Term }
 Term → Factor { MulOp Factor }
 Factor → [ UnaryOp ] Primary
 UnaryOp → - | !
 Primary → id | intlit | floatlit | true | false | ( Expression )
 RelOp → < | <= | > | >=
 AddOp → + | -
 MulOp → * | / | %
 EquOp → == | != 
"""



class Parser:
    def __init__(self, fn: str):
        """
        :param fn: a file_name str that it will read through
        lex: A lexer that will split up all the tokens in the file
        tg: The token generator for the Lexer
        currtok: The current Token being looked at
        ids: a dictionary of all the ids that have been declared
        """
        self.lex = Lexer(fn)
        self.tg = self.lex.token_generator()
        self.currtok = next(self.tg)
        self.ids = dict()
        self.functions = dict()

    def Program(self):
        """
        The highest level of the Parser will build up a list of 0 or more function definitions
        :return The ast of of the list of function definitions
        """
        funcs = list()
        while self.currtok[1].name in {"INT", "FLOAT", "BOOLEAN"}:
            func = self.FunctionDef()
            funcs.append(func)
        return Program(funcs)

    def FunctionDef(self):
        """
        A Function definition figure out its return type its identifier its required parameters  and all of the
        declarations and statements that are made withing the function body
        :return: This will return a abstract syntax tree
        :raises: SLUCSyntaxError for missing parentheses around the parameters following the functions identifier
        :raises: SLUCSyntaxError for missing Curly braces around the function body
        """
        type = self.Type()
        key = self.currtok[0]
        self.functions[self.currtok[0]] = "first_call"
        id = self.primary()
        self.functions[key] = type
        if self.currtok[1].name == "LPAREN":
            self.currtok = next(self.tg)
            params = self.Params()
            if self.currtok[1].name == "RPAREN":
                self.currtok = next(self.tg)
                if self.currtok[1].name == "LCURLY":
                    self.currtok = next(self.tg)
                    decs = self.Declarations()
                    states = self.Statements()
                    if self.currtok[1].name == "RCURLY":
                        self.currtok = next(self.tg)
                        return FunctionDef(type, id, params, decs, states)
                    raise SLUCSyntaxError("ERROR: Missing Right Curly Brace on line {0}"
                                          .format(str(self.currtok[2] - 1 - 1)))
                raise SLUCSyntaxError("ERROR: Missing Left Curly Brace on line {0}".format(str(self.currtok[2] - 1)))
            raise SLUCSyntaxError("ERROR: Missing Right Paren on line {0}".format(str(self.currtok[2] - 1)))
        raise SLUCSyntaxError("ERROR: Missing Left Paren on line {0}".format(str(self.currtok[2] - 1)))

    def Params(self):
        """
        This is where all the parameters of a function are put into a list the parameter id's are also added to the
        ids dictionary for the parser
        :return: This returns the parameters in the form of an abstract syntax tree
        """
        params = list()
        if self.currtok[1].name in {"INT", "FLOAT", "BOOLEAN"}:
            type = self.Type()
            self.ids[self.currtok[0]] = type
            id = self.primary()
            par = Param(type, id)
            params.append(par)
            while self.currtok[1].name in {"COMMA"}:
                self.currtok = next(self.tg)
                type = self.Type()
                self.ids[self.currtok[0]] = type
                id = self.primary()
                par = Param(type, id)
                params.append(par)
        return Params(params)

    def Declarations(self):
        """
        This will build up a list of declarations using the Declaration function from the Parser
        :return: an abstract syntax tree
        """
        decs = list()
        while self.currtok[1].name in {"INT", "FLOAT", "BOOLEAN"}:
            dec = self.Declaration()
            decs.append(dec)
        return DeclarationsExpr(decs)

    def Declaration(self):
        """
        This looks to declare identifiers withing the program and adds them to the ids dictionary in the Parser
        :return: the declaration as an abstract syntax tree
        :raises: SLUCSyntaxError if a semicolon is missing following the declaration
        :raises: SLUCSyntaxError if the identifiers has already been declaration
        :raises: SLUCSyntaxError if an identifier is not provided
        """
        type = self.Type()
        if self.currtok[1].name == "IDENT":
            self.ids[self.currtok[0]] = type
            id = self.primary()

            if self.currtok[1].name == "SEMI":
                self.currtok = next(self.tg)
                return DeclarationExpr(type, id)

            raise SLUCSyntaxError("ERROR Missing Semicolon on line {0}".format(str(self.currtok[2] - 1)))
        raise SLUCSyntaxError("ERROR Missing Identifier on line {0}".format(str(self.currtok[2] - 1)))

    def Type(self):
        """
        This is used to get a type for function returns, params, declarations
        :return: an abstract syntax tree
        :raises: if we are not given a valid type
        """
        if self.currtok[1].name in {"INT", "FLOAT", "BOOLEAN"}:
            type = self.currtok[0]
            self.currtok = next(self.tg)
            return type
        raise SLUCSyntaxError("ERROR: Unexpected token {0} on line {1}".
                              format(self.currtok[1], str(self.currtok[2] - 1)))

    def Statements(self):
        """
        Used for when there is zero or more statements it builds up a list of statments
        :return: an abstract syntax tree
        """
        states = list()
        while self.currtok[1].name in {"SEMI", "LCURLY", "IDENT", "if", "print", "while", "return"}:
            state = self.Statement()
            states.append(state)
        return StatementsStmt(states)

    def Statement(self):
        """
        leads to the correct statement token
        :return: the ast that matches with the statement token
        :raises: SLUCSyntaxError If not a valid statement token is given it
        """
        if self.currtok[1].name == "SEMI":
            self.currtok = next(self.tg)
            return semicolon()
        if self.currtok[1].name == "LCURLY":
            return self.Block()
        if self.currtok[1].name == "IDENT":
            if self.functions.get(self.currtok[0]) is None:
                return self.Assignment()
            else:
                return self.FunctionCall()
        if self.currtok[1].name == "if":
            return self.IfStatement()
        if self.currtok[1].name == "print":
            return self.PrintStmt()
        if self.currtok[1].name == "while":
            return self.WhileStatement()
        if self.currtok[1].name == "return":
            return self.ReturnStmt()

        raise SLUCSyntaxError("ERROR: Unexpected token {0} on line {1}".
                              format(self.currtok[1], str(self.currtok[2] - 1)))

    def ReturnStmt(self):
        """
        With the key word return it followed by an expression and semi colon
        :return: the abstract syntax tree
        :raises: SLUCSyntaxError is a missing semicolon following the return statement
        """
        self.currtok = next(self.tg)
        express = self.Expression()
        if self.currtok[1].name == "SEMI":
            self.currtok = next(self.tg)
            return returnStmt(express)
        raise SLUCSyntaxError("ERROR: Missing Semicolon on line {0}".format(str(self.currtok[2] - 1)))

    def Block(self):
        """
        A set of 0 or more statements withing curly braces
        :return: the abstract syntax tree
        :raises: SLUCSyntaxError is a missing a right curly brace to close the block
        """
        self.currtok = next(self.tg)
        statements = self.Statements()
        if self.currtok[1].name == "RCURLY":
            self.currtok = next(self.tg)

            return BlockExpr(statements.get_lst())

        raise SLUCSyntaxError("ERROR: Right Curly Brace on line {0}".format(str(self.currtok[2] - 1)))

    def Assignment(self):
        """
        Setting a value to an identifier that is in the ids dictionary
        :return: the abstract syntax tree
        :raises: SLUCSyntaxError is a missing semicolon following the assigned value
        :raises: SLUCSyntaxError is a missing an (=) following the identifier
        """
        id = self.primary()
        if self.currtok[1].name == "DECLERATION":
            self.currtok = next(self.tg)
            if self.functions.get(self.currtok[0]) is not None:

                express = self.FunctionCall()
                return assignmentStmt(id, express)
            else:
                express = self.Expression()

                if self.currtok[1].name == "SEMI":
                    self.currtok = next(self.tg)
                    return assignmentStmt(id, express)
                raise SLUCSyntaxError("ERROR: Missing Semicolon on line {0}".format(str(self.currtok[2] - 1)))
        raise SLUCSyntaxError("ERROR: Missing assignment on line {0}".format(str(self.currtok[2] - 1)))

    def IfStatement(self):
        """
        Given the key word if has an expression as a condition for the if then win a set of parentheses
        and followed by an statement and can end with the key world else followed by a statement
        :return: an abstract syntax tree
        :raises: SLUCSyntaxError missing a left parenthesise for following the key word if
        :raises: SLUCSyntaxError missing a right parenthesise for following the expression
        """
        self.currtok = next(self.tg)
        if self.currtok[1].name == "LPAREN":
            self.currtok = next(self.tg)
            express = self.Expression()
            if self.currtok[1].name == "RPAREN":
                self.currtok = next(self.tg)
                state = self.Statement()
                if self.currtok[1].name == "else":
                    self.currtok = next(self.tg)
                    state2 = self.Statement()
                    return ifelseStmt(express, state, state2)
                else:
                    return ifStmt(express, state)
            raise SLUCSyntaxError("ERROR: Missing right paren on line {0}".format(str(self.currtok[2] - 1)))
        raise SLUCSyntaxError("ERROR: Missing left paren on line {0}".format(str(self.currtok[2] - 1)))

    def WhileStatement(self):
        """
         Given the key word while has an expression as a condition for the if then within a set of parentheses and
         followed by a statement
        :return: an abstract syntax tree
        :raises: SLUCSyntaxError missing a left parenthesise for following the key word while
        :raises: SLUCSyntaxError missing a right parenthesise for following the expression
        """
        self.currtok = next(self.tg)
        if self.currtok[1].name == "LPAREN":
            self.currtok = next(self.tg)
            express = self.Expression()
            if self.currtok[1].name == "RPAREN":
                self.currtok = next(self.tg)
                state = self.Statement()
                return whileStmt(express, state)
            raise SLUCSyntaxError("ERROR: Missing right paren on line {0}".format(str(self.currtok[2] - 1)))
        raise SLUCSyntaxError("ERROR: Missing left paren on line {0}".format(str(self.currtok[2] - 1)))

    def PrintStmt(self):
        """
        This takes a list of print arguments separated by commas and surrounded by parentheses all following the key
        word print
        :return: an abstract syntax tree
        :raises: SLUCSyntaxError missing a left parenthesise for following the key word print
        :raises: SLUCSyntaxError missing a right parenthesise for following the set of print arguments or a comma
        """
        args = list()
        self.currtok = next(self.tg)
        if self.currtok[1].name == "LPAREN":
            self.currtok = next(self.tg)
            arg = self.PrintArg()
            args.append(arg)
            while self.currtok[1].name == "COMMA":
                self.currtok = next(self.tg)
                arg = self.PrintArg()
                args.append(arg)

            if self.currtok[1].name == "RPAREN":
                self.currtok = next(self.tg)
                if self.currtok[1].name == "SEMI":
                    return printstmtStmt(args)
                raise SLUCSyntaxError("ERROR: Missing right semicolon line {0}".format(str(self.currtok[2] - 1)))
            raise SLUCSyntaxError("ERROR: Missing right paren or a comma line {0}".format(str(self.currtok[2] - 1)))
        raise SLUCSyntaxError("ERROR: Missing left paren on line {0}".format(str(self.currtok[2] - 1)))

    def PrintArg(self):
        """
        The items that are found within a print statements can be strings expressions or function calls
        :return: an abstract syntax tree
        """
        if self.currtok[1].name == "STRING_LIT":
            arg = String_LitExpr(self.currtok[0])
            self.currtok = next(self.tg)
            return printArg(arg)
        if self.functions.get(self.currtok[0]) is not None:
            arg = self.FunctionCall()
            return printArg(arg)
        arg = self.Expression()
        return printArg(arg)

    def FunctionCall(self):
        """
        If a function is called it is the list of required params separated by commas all surrounded by
        parentheses
        :return: an abstract syntax tree
        :raises: SLUCSyntaxError missing a separating comma between two parameters
        :raises: SLUCSyntaxError missing a left parenthesise for following the key word print
        :raises: SLUCSyntaxError missing a right parenthesise for following the set of print arguments or a comma
        """
        id = self.currtok[0]
        self.currtok = next(self.tg)
        if self.currtok[1].name == "LPAREN":
            self.currtok = next(self.tg)
            params = list()

            while self.currtok[1].name in {"BOOL", "INTLIT", "IDENT", "REAL"}:
                param = self.Expression()
                if self.currtok[1].name != "RPAREN":
                    if self.currtok[1].name == "COMMA":
                        self.currtok = next(self.tg)
                    else:
                        raise SLUCSyntaxError("ERROR: Missing comma on line {0}".format(str(self.currtok[2] - 1)))
                params.append(param)

            if self.currtok[1].name == "RPAREN":
                self.currtok = next(self.tg)
                return FuncIDExpr(id, params)

            raise SLUCSyntaxError("ERROR: Missing right paren on line {0}".format(str(self.currtok[2] - 1)))
        raise SLUCSyntaxError("ERROR: Missing left paren on line {0}".format(str(self.currtok[2] - 1)))

    def Expression(self, paren=False):
        """
        One conjunction expression possibly matched more conjunctions expression separated by ||
        :return: an abstract syntax tree
        """
        left = self.Conjunction(paren)
        while self.currtok[1].name == "OR":
            op = self.currtok[0]
            self.currtok = next(self.tg)
            right = self.Conjunction()
            left = BinaryExpr(op, left, right, paren)
        return left

    def Conjunction(self, paren=False):
        """
        One equality expression possibly matched more equality expression separated by &&
        :return: an abstract syntax tree
        """
        left = self.Equality(paren)
        while self.currtok[1].name == "AND":
            op = self.currtok[0]
            self.currtok = next(self.tg)
            right = self.Equality(paren)
            left = BinaryExpr(op, left, right, paren)
        return left

    def Equality(self, paren=False):
        """
        One relation expression possibly matched one more relation expression separated by == or !=
        :return: an abstract syntax tree
       """
        left = self.Relation(paren)
        if self.currtok[1].name in {"EQULITY", "NOTEQUAL"}:
            op = self.currtok[0]
            self.currtok = next(self.tg)
            right = self.Relation(paren)
            left = BinaryExpr(op, left, right, paren)
        return left

    def Relation(self, paren=False):
        """
        One adddition expression possibly matched one more adddition expression separated by > , <, >= or <=
        :return: an abstract syntax tree
        """
        left = self.Addition(paren)
        if self.currtok[1].name in {"GREATERTHAN", "LESSTHAN", "LET", "GET"}:
            op = self.currtok[0]
            self.currtok = next(self.tg)
            right = self.Addition(paren)
            left = BinaryExpr(op, left, right, paren)
        return left

    def Addition(self, paren=False):
        """
        One term expression possibly matched more term expression separated by + or -
        :return: an abstract syntax tree
        """
        left = self.Term(paren)
        while self.currtok[1].name in {"PLUS", "MINUS"}:
            op = self.currtok[0]
            self.currtok = next(self.tg)
            right = self.Term(paren)
            left = BinaryExpr(op, left, right, paren)
        return left

    def Term(self, paren=False):
        """
        One Factor expression possibly matched more Factor expression separated by *, / or %
        :return: an abstract syntax tree
        """
        left = self.Factor()
        while self.currtok[1].name in {"TIMES", "DIVISION", "MOD"}:
            op = self.currtok[0]
            self.currtok = next(self.tg)
            right = self.Factor()
            left = BinaryExpr(op, left, right, paren)
        return left

    def Factor(self):
        """
        A primary expression that is preceded a !, - or nothing at all
        :return: an abstract syntax tree
        """
        if self.currtok[1].name in {"MINUS", "NOT"}:
            op = self.currtok[0]
            self.currtok = next(self.tg)
            prime = self.primary()
            return Factor(op, prime)
        return self.primary()

    def primary(self):
        """
        Gets the back an identifier, an intlit, boolean real or another expression that is surrounded by parentheses
        :return: an abstract syntax tree
        :raises: SLUCSyntaxError if an identifier that was passed in is not been declared in the ids dictionary or
        function dictionary
        :raises: SLUCSyntaxError if a right parenthesise is missing from the cases when an (expression) occurs
        :raises SLUCSyntaxError if an invalid token has been passed into the primary
        """
        if self.currtok[1].name == "IDENT":
            tmp = self.currtok
            if self.functions.get(tmp[0]) is not "first_call" and self.functions.get(tmp[0]) is not None:
                func = self.FunctionCall()
                return func

            elif self.ids.get(tmp[0]) is not None or self.functions.get(tmp[0]) is "first_call":
                self.currtok = next(self.tg)
                return IDExpr(tmp[0])
            else:
                raise SLUCSyntaxError(
                    "ERROR: Given ID {0} was not declared above on line {1}".format(tmp[0], str(self.currtok[2] - 1)))

        if self.currtok[1].name == "INTLIT":
            tmp = self.currtok
            self.currtok = next(self.tg)
            return IntLitExpr(tmp[0])

        if self.currtok[1].name == "BOOL":
            tmp = self.currtok[0]
            self.currtok = next(self.tg)
            return BoolExpr(tmp[0])

        if self.currtok[1].name == "REAL":
            tmp = self.currtok
            self.currtok = next(self.tg)
            return Real_Expr(tmp[0])

        if self.currtok[1].name == "STRING_LIT":
            tmp = self.currtok
            self.currtok = next(self.tg)
            return String_LitExpr(tmp[0])

        if self.currtok[1].name == "LPAREN":
            self.currtok = next(self.tg)
            tree = self.Expression(True)
            if self.currtok[1].name == "RPAREN":
                self.currtok = next(self.tg)
                return tree
            else:
                raise SLUCSyntaxError("ERROR: Missing right paren on line {0}".format(str(self.currtok[2] - 1)))
        raise SLUCSyntaxError("ERROR: Unexpected token {0} on line {1}".
                              format(self.currtok[1], str(self.currtok[2] - 1)))


# used for raising errors in the parser
class SLUCSyntaxError(Exception):
    def __init__(self, message: str):
        Exception.__init__(self)
        self.message = message

    def __str__(self):
        return self.message


# main program setup to print out the parser nicely
if __name__ == '__main__':

    syargs = sys.argv
    p = Parser(syargs[1])
    try:
        t = p.Program()
        t.type_check()
        t.eval()
    except (IOError, SLUCSyntaxError, slutype, slusyn) as err:
        print(err)

        split_patt = re.compile("""
                               (;)     |
                               ([\}{])      """, re.VERBOSE)

        """  t = str(t)
        t = split_patt.split(t)
        t = list(filter(None, t))
        
        tab_count = 0
        special_case = False
        print("")
        for token in t:
            special_case = False
            if token[0:2] == "if" and token.find(")") < len(token):
                special_case = True
                x = token.find(")")
                spaces1 = "  " * tab_count
                spaces2 = "  " * (tab_count + 1)
                str1 = token[0:x + 1]
                str2 = token[x+1:]
                print(spaces1, str1)
                print(spaces2, str2, end='')
    
            if token[0:4] == "else" and token.find("{") is -1:
                special_case = True
                x = 3
                spaces1 = "  " * tab_count
                spaces2 = "  " * (tab_count + 1)
                str1 = token[0:x + 1]
                str2 = token[x + 1:]
                print(spaces1, str1)
                print(spaces2, str2, end='')
    
            if token[0:4] == "while" and token.find(")") < len(token):
                special_case = True
                x = token.find(")")
                spaces1 = "  " * tab_count
                spaces2 = "  " * (tab_count + 1)
                str1 = token[0:x + 1]
                str2 = token[x + 1:]
                print(spaces1, str1)
                print(spaces2, str2, end='')
    
            if token in "{":
                tab_count += 1
    
            if token == "}":
                tab_count -= 1
    
            if special_case is False and token not in {"}", ";", "{"}:
                spaces = "  " * tab_count
                print(spaces, token, end='')
            if token == "}":
                spaces = "  " * tab_count
                print(spaces, token)
    
            if token in {"{", ";"}:
                print(token)
    """

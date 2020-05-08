from typing import List, Union
import interp_info

functions = dict()
function_stack = list()
type_checker = list()

type_dict = dict()
type_dict["int"] = int
type_dict["bool"] = bool
type_dict["float"] = float


class type_env:
    def __init__(self):
        self.decls = dict()
        self.ret_type = None
        self.func_name = None


class environment:
    def __init__(self, func):

        self.assigned_val = dict()
        # function level
        self.ret = None

        self.func = func


class Expr:
    def eval(self):
        pass

    def type_check(self):
        pass


class semicolon(Expr):
    """
    Just do deal with the SemiColon Cases at the end of lines in Statements
    """
    def __init__(self):
        self.semi = ";"

    def __str__(self):
        return self.semi


class IntLitExpr(Expr):
    """
    Deals with Integer Expressions
    """
    def __init__(self, intlit: str):
        self.intlit = int(intlit)

    def __str__(self):
        return str(self.intlit)

    def eval(self):
        return self.intlit

    def type_check(self):
        return int


class Real_Expr(Expr):
    """
    Deals with Real Expressions
    """
    def __init__(self, real: str):
        self.real = float(real)

    def __str__(self):
        return str(self.real)

    def eval(self):
        return self.real

    def type_check(self):
        return float


class IDExpr(Expr):
    """
     Deals with ID Expressions
    """
    def __init__(self, id: str):
        self.id = id

    def __str__(self):
        return self.id

    def eval(self):
        return function_stack[len(function_stack) - 1].assigned_val[self.id]

    def type_check(self):

        if type_checker[len(type_checker) - 1].decls.get(self.id) is None:
            if functions[self.id] is None:
                raise SLUCSyntaxError("ERROR: {0} has not been declared".format(id))
            return type_dict[functions[self.id].type]

        return type_checker[-1].decls[self.id]


class FuncIDExpr(Expr):
    """
    For when a function Id is called
    """
    def __init__(self, id: str, params: List[Expr]):
        self.id = id
        self.params = params

    def __str__(self):
        param = "{0}({1}".format(str(self.id), str(self.params[0]))
        for x in range(1, len(self.params)):
            param = "{0},{1}".format(param, str(self.params[x]))
        param = param + ")"
        return param

    def eval(self):

        func = functions[str(self.id)]
        env = environment(str(func.id))
        env.assigned_val = function_stack[(len(function_stack) - 1)].assigned_val
        function_stack.append(env)
        func.params.eval(self.params)
        func.eval()
        hold = function_stack[len(function_stack) - 1]
        function_stack.remove(hold)
        return hold.ret

    def type_check(self):
        func = functions.get(self.id)
        params = func.params.params
        w = list()
        for val in params:
            w.append(val.id)

        if len(w) > len(self.params):
            raise SLUCTypeError("ERROR not enough values passed into function {0}".format(self.id))

        if len(w) < len(self.params):
            raise SLUCTypeError("ERROR Too many  values passed into function {0}".format(self.id))

        for index in range(len(w)):
            ident = None
            for fun in type_checker:
                if str(fun.func_name) == str(func.id):
                    ident = fun.decls.get(str(w[index]))

            val = self.params[index].type_check()

            if ident == bool and val != bool:
                raise SLUCTypeError("ERROR Expected {0}  but {1} passed into function ".format(str(ident), str(val)))

            if ident != bool and val == bool:
                raise SLUCTypeError("ERROR Expected {0}  but {1} passed into function ".format(str(ident), str(val)))

        return type_dict[func.type]


class String_LitExpr(Expr):
    """
     Deals with String Expressions
    """
    def __init__(self, string: str):
        self.string = string

    def __str__(self):
        return self.string

    def eval(self):
        return self.string[1:len(self.string) - 1]

    def type_check(self):
        return str


class BoolExpr(Expr):
    """
    Deals With Boolean Expressions
    """
    def __init__(self, boolean: str):

        if boolean is "t":
            self.boolean = True

        else:
            self.boolean = False

    def __str__(self):
        return str(self.boolean)

    def eval(self):
        return self.boolean

    def type_check(self):
        return bool


class BinaryExpr(Expr):
    """
    Used for forms of Equations
    """
    def __init__(self, op: str, left: Expr, right: Expr, paren=False):
        """
        :param op: The operation for the Expression
        :param left: The left Side of the operator
        :param right: The right side of the operator
        """
        self.op = op
        self.left = left
        self.right = right
        self.paren = paren

    def __str__(self):
        if self.paren:
            return "({0} {1} {2})".format(str(self.left), self.op, str(self.right))
        else:
            return "{0} {1} {2}".format(str(self.left), self.op, str(self.right))

    def eval(self):
        return interp_info.bin_express[self.op](self.left.eval(), self.right.eval())

    def type_check(self):

        if self.right.type_check() is str or self.left.type_check() is str:
            raise SLUCTypeError("ERROR: String Can't be used in Binary Operations")

        if self.op in {"+", "-", "*", "/"}:
            if self.right.type_check() is bool or self.left.type_check() is bool:
                raise SLUCTypeError("ERROR: Expected a non bool values for the {0} operator but got {1} and {2}".
                                      format(self.op, str(self.left), str(self.right)))
            else:
                if self.right.type_check() is float or self.left.type_check() is float:
                    return float
                else:
                    return int

        elif self.op in {"<", ">", "==", "!=", "<=", ">="}:
            if self.right.type_check() is bool or self.left.type_check() is bool:
                raise SLUCTypeError("ERROR: Expected a non bool values for the {0} operator but got {1} and {2}".
                                      format(self.op, str(self.left), str(self.right)))
            else:
                return bool

        elif self.op in {"%", ">>", "<<"}:
            return int

        elif self.op in {"&&", "||"}:
            if self.right.type_check() is not bool or self.left.type_check() is not bool:
                raise SLUCTypeError("ERROR: Expected bool values for the {0} operator but got {1} and {2}".
                                      format(self.op, str(self.left), str(self.right)))
            else:
                return bool
        else:
            pass


class Factor(Expr):
    """
    For Noting values and making Negatives
    """
    def __init__(self, op: str, primary: BinaryExpr):
        """
        :param op: The symbol in front of the Expression
        :param primary: The Expression
        """
        self.op = op
        self.prime = primary

    def __str__(self):
        return "{0}{1}".format(self.op, str(self.prime))

    def eval(self):
        return interp_info.unary_express[self.op](self.prime.eval())

    def type_check(self):

        if self.prime.type_check() is str:
            raise SLUCTypeError("ERROR: String Can't be used in Unary Operations")

        if self.op == "!":
            if self.prime.type_check() is not bool:
                raise SLUCTypeError("ERROR: Expected a bool value for the ! operator but got {0}".
                                      format(str(self.prime)))
            else:
                return bool

        if self.op == "-":
            if self.prime.type_check() is bool:
                raise SLUCTypeError("ERROR: Expected a float/int value for the - operator but got {0}".
                                      format(str(self.prime)))
            else:
                return self.prime.type_check()


class printArg:
    """
    The argument for the Print Statement
    """
    def __init__(self, arg: Union[BinaryExpr, String_LitExpr, FuncIDExpr]):
        """
        :param arg: Is either a Binary Expression or a String for the argument
        """
        self.arg = arg

    def __str__(self):
        return "{0}".format(str(self.arg))

    def eval(self):
        print(self.arg.eval(), end=' ')

    def type_check(self):
        self.arg.type_check()


class Stmt:
    def eval(self):
        pass

    def type_check(self):
        pass


class printstmtStmt(Stmt):
    """
       Corresponds to print("Hello")
       the print Expression
    """
    def __init__(self, arg: List[printArg]):
        """
        :param arg: A list of print Arguments
        """
        self.arg = arg

    def __str__(self):
        states = "print({0}".format(str(self.arg[0]))
        for x in range(1, len(self.arg)):
            states = "{0}, {1}".format(states, str(self.arg[x]))
        states = states + ")"

        return states

    def eval(self):
        for arg in self.arg:
            arg.eval()
        print()

    def type_check(self):
        for arg in self.arg:
            arg.type_check()


class whileStmt(Stmt):
    """
    What makes up a while Statement
    """
    def __init__(self, express: BinaryExpr, state: Stmt):
        """
        :param express: The expression for the while loop to run
        :param state: The Body of the While loop
        """
        self.express = express
        self.state = state

    def __str__(self):
        return "while({0}){1}".format(str(self.express), str(self.state))

    def eval(self):
        while self.express.eval():
            self.state.eval()

    def type_check(self):
        express = self.express.type_check()
        if express is not bool:
            raise SLUCTypeError(
                "ERROR: Expect a boolean for an if statement argument but got {0}".format(str(express)))
        self.state.type_check()


class ifStmt(Stmt):
    """
    What makes up an if statement
    elsestmt: Stmt = None
    """
    def __init__(self, express: BinaryExpr, state: Stmt):
        """
        :param express: The requirement expression for the if Statement
        :param state: The body of the if statement
        """
        self.express = express
        self.state = state

    def __str__(self):
        return "if({0}){1}".format(str(self.express), str(self.state))

    def eval(self):
        if self.express.eval():
            self.state.eval()

    def type_check(self):
        express = self.express.type_check()
        if express is not bool:
            raise SLUCTypeError("ERROR: Expect a boolean for an if statement argument but got {0}".
                                  format(str(express)))
        self.state.type_check()


class ifelseStmt(Stmt):
    """
    If with and else statement
    """
    def __init__(self, express: BinaryExpr, state: Stmt, state2: Stmt):
        """
        :param express: The requirement for the if statement
        :param state: The body of the if statement
        :param state2: The body of the else statement
        """
        self.express = express
        self.state = state
        self.state2 = state2

    def __str__(self):
        return "if({0}){1}else{2}".format(str(self.express), str(self.state), str(self.state2))

    def eval(self):
        if self.express.eval():
            self.state.eval()

        else:
            self.state2.eval()

    def type_check(self):
        express = self.express.type_check()
        if express is not bool:
            raise SLUCTypeError(
                "ERROR: Expect a boolean for an if statement argument but got {0}".format(str(express)))
        self.state.type_check()
        self.state2.type_check()


class assignmentStmt(Stmt):
    """
    Assigning a identifier a value
    """
    def __init__(self, id: IDExpr, assign: Union[BinaryExpr, FuncIDExpr]):
        """
        :param id: The identifier you are assigning
        :param assign: The assignment of the identifier
        """
        self.id = id
        self.assign = assign

    def __str__(self):
        return "{0} = {1};".format(str(self.id), str(self.assign))

    def eval(self):

        func = function_stack[-1].func
        type = None
        for fun in type_checker:
            if fun.func_name == func:
                type = fun.decls[str(self.id)]
        if type == int:
            function_stack[-1].assigned_val[str(self.id)] = int(self.assign.eval())
        else:
            function_stack[-1].assigned_val[str(self.id)] = self.assign.eval()

    def type_check(self):
        id = type_checker[-1].decls.get(str(self.id))
        val = self.assign.type_check()
        if type_checker[-1].decls.get(str(self.id)) is None:
            raise SLUCSyntaxError("ERROR: ID {0} has not been declared".format(str(id)))
        else:
            if id in {int, float} and val == bool:
                raise SLUCTypeError("ERROR: Expected {0} for {1} but got a {2}".
                                      format(str(id), str(self.id), str(val)))

            if id == bool and val in {int, float}:
                raise SLUCTypeError("ERROR: Expected {0} for {1} but got a {2}".
                                      format(str(id), str(self.id), str(val)))
            if val == str:
                raise SLUCTypeError("ERROR: Expected {0} for {1} but got a {2}".
                                      format(str(id), str(self.id), str(val)))


class BlockExpr(Stmt):
    """
    A body of Statements
    """
    def __init__(self, statements: List[Stmt]):
        """
        :param statements: A list of Statements in the block
        """
        self.statements = statements

    def __str__(self):
        states = "{"
        for expr in self.statements:
            states = "{0}{1}".format(states, str(expr))
        states = states+"}"
        return states

    def eval(self):
        for state in self.statements:
            state.eval()

    def type_check(self):
        for state in self.statements:
            state.type_check()


class returnStmt(Stmt):
    """
    What we are returning
    """
    def __init__(self, express: BinaryExpr):
        """
        :param express: The Expression for each statement
        """
        self.express = express

    def __str__(self):
        return "return {0};".format(str(self.express))

    def eval(self):
        function_stack[len(function_stack) - 1].ret = self.express.eval()

    def type_check(self):
        ret = type_checker[len(type_checker) - 1].ret_type
        val = self.express.type_check()

        if val is str:
            raise SLUCTypeError("ERROR: String return type not implemented")

        if ret in {int, float} and val == bool:
            raise SLUCTypeError("ERROR: Expected return type {0} but got a {1}".format(str(ret), str(val)))
        if ret == bool and val in {int, float}:
            raise SLUCTypeError("ERROR: Expected return type {0} but got a {1}".format(str(ret), str(val)))
        if ret == int and val == float:
            raise SLUCTypeError("ERROR: Expected return type {0} but got a {1}".format(str(ret), str(val)))

        return val


class StatementsStmt(Stmt):
    """
    All the different types of statements that are possible
    """
    def __init__(self, statements: List[Union[printstmtStmt, returnStmt, BlockExpr, ifStmt,
                                              ifelseStmt, whileStmt, assignmentStmt]]):
        """
        :param statements: A List of all the types of Statements
        """
        self.statements = statements

    def get_lst(self):
        return self.statements

    def __str__(self):
        states = ""
        for expr in self.statements:
            states = "{0}{1}".format(states, str(expr))
        return states

    def eval(self):
        for state in self.statements:
            state.eval()

    def type_check(self):
        for state in self.statements:
            state.type_check()


class DeclarationExpr(Expr):
    """
    Declaring an Identifier
    """
    def __init__(self, type: str, id: IDExpr):
        """
        :param type: The type for the Identifier
        :param id: The actual Identifier as well
        """
        self.type = type
        self.id = id

    def __str__(self):
        return "{0} {1};".format(self.type, str(self.id))

    def type_check(self):
        if type_checker[len(type_checker) - 1].decls.get(str(self.id)) is None:
            type_checker[len(type_checker) - 1].decls[str(self.id)] = type_dict[str(self.type)]

        else:
            raise SLUCSyntaxError("ERROR: ID {0} has already been declared".format(str(self.id)))


class DeclarationsExpr(Expr):
    """
    All the Declaration Expressions
    """
    def __init__(self, decs: List[DeclarationExpr]):
        """
        :param decs: A List of the declarations made
        """
        self.decs = decs

    def __str__(self):
        dec = ""
        for expr in self.decs:
            dec = dec + str(expr)
        return dec

    def type_check(self):
        for dec in self.decs:
            dec.type_check()


class Param(Expr):
    """
    Defining a parameter for a function
    """
    def __init__(self, type: str, id: IDExpr):
        """
        :param type: The type of the Parameter
        :param id: The identifier for the Parameter
        """
        self.type = type
        self.id = id

    def __str__(self):
        return "{0} {1}".format(self.type, str(self.id))

    def eval(self, val: int = None):
        function_stack[-1].assigned_val[str(self.id)] = val

    def type_check(self):
        type_checker[len(type_checker) - 1].decls[str(self.id)] = type_dict[str(self.type)]


class Params(Expr):
    """
    All the parameters
    """
    def __init__(self, params: List[Param]):
        """
        :param params: The List of the parameters
        """
        self.params = params

    def __str__(self):
        param = ""
        for expr in self.params:
            param = param + str(expr) + " "
        return param

    def eval(self, values: List[Expr] = None):

        for x in range(len(self.params)):
            val = values[x].eval()

            self.params[x].eval(val)

    def type_check(self):
        for param in self.params:
            param.type_check()


class FunctionDef:
    """
    What makes up a function for
    """
    def __init__(self, type: str, id: IDExpr, params: Params, decls: DeclarationsExpr, stmts: StatementsStmt):
        """
        :param type: The return type for the function
        :param id: THe id of the function
        :param params: The arguments parameters of the functions
        :param decls: The List declaration made in the function
        :param stmts: The List of statements made in the functions
        """
        self.type = type
        self.id = id
        self.params = params
        self.decls = decls
        self.stmts = stmts
        functions[str(self.id)] = self

    def __str__(self):
        mystring = "{0} {1}({2})".format(self.type, str(self.id), str(self.params))
        mystring += "{"
        mystring += "{0}{1}".format(str(self.decls), str(self.stmts))
        mystring += "}"
        return mystring

    def eval(self):
        self.stmts.eval()

    def type_check(self):
        env = type_env()
        env.ret_type = type_dict[self.type]
        env.func_name = str(self.id)
        type_checker.append(env)
        self.params.type_check()
        self.decls.type_check()
        self.stmts.type_check()


class Program:
    def __init__(self, funcs: List[FunctionDef]):
        """
        :param funcs: A list of all the functions in the program
        """
        self.funcs = funcs

    def __str__(self):
        func = ""
        for expr in self.funcs:
            func = func + str(expr)
        return func

    def eval(self):
        for func in self.funcs:
            if str(func.id) == "main":
                function_stack.append(environment("main"))
                func.eval()

    def type_check(self):
        for func in self.funcs:
            func.type_check()


class SLUCSyntaxError(Exception):
    def __init__(self, message: str):
        Exception.__init__(self)
        self.message = message

    def __str__(self):
        return self.message


class SLUCTypeError(Exception):
    def __init__(self, message: str):
        Exception.__init__(self)
        self.message = message

    def __str__(self):
        return self.message

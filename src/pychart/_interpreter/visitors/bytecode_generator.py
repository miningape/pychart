
from typing import Any, Dict, List, Callable

from src.pychart._interpreter.ast_nodes.statement import *
from src.pychart._interpreter.ast_nodes.expression import *

from src.pychart._interpreter.token_type.token_type_enum import TokenType
from src.pychart._interpreter.token_type.token import Token
import  src.pychart.bytecode.bytecodes as bt

def remove_inner_lists(obj: List[Any]):
    result = []
    for val in obj:
        if isinstance(val, list):
            result += val
        else:
            result.append(val)
    return result

class BytecodeGeneratorState:
    variables : Dict[str, Any] = {}
    bytecode  : List[bt.Bytecode] = []
    statements: List[Stmt]     = None
    loop_id   : str

    def __init__(self, variables: Dict[str, Any],
            bytecode: List[bt.Bytecode], statements: List[Stmt], loop_id: str):
        self.variables  = variables
        self.bytecode   = bytecode
        self.statements = statements
        self.loop_id    = loop_id

class BytecodeGeneratorIdentifier:
    is_function: bool = False
    name: bt.Identifier
    def __init__(self, name: str, is_function: bool):
        self.is_function = is_function
        self.name        = bt.Identifier(name)


class BytecodeExpression:
    callback: Callable
    def __init__(self, callback: Callable):
        self.callback = callback

    def __call__(self, identifier: bt.Identifier):
        assert isinstance(identifier, bt.Identifier) or identifier is None
        return self.callback(identifier)

def is_token(operator, token: TokenType):
    return operator.token_type == token

class BytecodeGenerator(ExprVisitor, StmtVisitor):
    state_stack : list[Any]     = []
    variables  : dict[str, BytecodeGeneratorIdentifier] = {}
    bytecode   : list[bt.Bytecode] = []
    statements : list[Stmt]     = None
    loop_id    : str = None

    # this is used for generated names
    generated_id : int          = 0

    def __init__(self, statements: list[Stmt], native_functions: list[str]):
        self.statements = statements
        for name in native_functions:
            self.variables[name] = BytecodeGeneratorIdentifier(name, True)

    def push_state(self, statements: list[Stmt]):
        state_obj = BytecodeGeneratorState(self.variables,
                self.bytecode, self.statements, self.loop_id)

        self.state_stack.append(state_obj)
        self.variables  = {}
        self.bytecode   = []
        self.statements = statements

    def pop_state(self):
        if len(self.state_stack) == 0:
            return None
        current_state = BytecodeGeneratorState(self.variables,
                self.bytecode, self.statements, self.loop_id)
        old_state = self.state_stack.pop()
        self.variables  = old_state.variables
        self.bytecode   = old_state.bytecode
        self.statements = old_state.statements
        self.loop_id    = old_state.loop_id
        return current_state

    def next_id(self) -> int:
        val = self.generated_id
        self.generated_id += 1
        return val

    def get_identifier(self, name: str):
        if name in self.variables:
            return self.variables[name]
        for state in reversed(self.state_stack):
            if name in state.variables:
                return state.variables[name]
        return None

    def push_function(self, name: str):
        if name in self.variables:
            raise RuntimeError(f"Variable {name} is already defined")

        if self.get_identifier(name) is not None:
            print(f"Warning: Shadowing declaration of variable {name}")

        actual_name = str(len(self.state_stack)) + name
        self.variables[name] = BytecodeGeneratorIdentifier(actual_name, True)

    def push_identifier(self, name: str):
        if name in self.variables:
            raise RuntimeError(f"Variable {name} is already defined")

        if self.get_identifier(name) is not None:
            print(f"Warning: Shadowing declaration of variable {name}")

        actual_name = str(len(self.state_stack)) + name
        self.variables[name] = BytecodeGeneratorIdentifier(actual_name, False)

    def push(self, bytecode: bt.Bytecode):
        self.bytecode.append(bytecode)

    def gen_bytecode_expression(self, code: BytecodeExpression):
        ([create_temp, set_value], temporary) = self.gen_internal_bytecode_expression(code)
        self.push(create_temp)
        self.push(set_value)
        return temporary

    def gen_internal_bytecode_expression(self, code: BytecodeExpression):
        temporary_name = '.tmp' + str(self.next_id())
        temporary   = bt.Identifier(temporary_name)
        create_temp = bt.Create(temporary)
        set_value   = code(temporary)
        return ([create_temp, set_value], temporary)

    def generate(self, keep_labels: bool = False):
        return self.internal_generate(True, keep_labels)

    def internal_generate(self, should_solve: bool, keep_labels: bool = False):
        try:
            for statement in self.statements:
                statement(self)
        except RuntimeError as err:
            print(f"Error: {err}")
            print("Exiting...")
            return None
        if should_solve:
            self.bytecode = bt.solve_block(self.bytecode, keep_labels=keep_labels)
        return self.bytecode

    def expression(self, stmt: Expression) -> Any:
        expr = stmt.expr(self)
        if isinstance(expr, bt.Bytecode):
            self.push(expr)
        elif bt.is_list_of(bt.Bytecode, expr):
            for code in expr:
                self.push(code)
        elif isinstance(expr, BytecodeExpression):
            self.push(expr(None))

    def let(self, stmt: Let) -> Any:
        name = stmt.name.lexeme
        self.push_identifier(name)
        identifier = self.get_identifier(name).name
        self.push(bt.Create(identifier))

        if stmt.initializer is not None:
            value = stmt.initializer(self)
            if isinstance(value, Literal):
                self.push(bt.Push(identifier, bt.Value(value.value)))
            elif isinstance(value, Variable):
                value_name = self.get_identifier(value.name.lexeme).name
                self.push(bt.Push(identifier, value_name))
            elif isinstance(value, BytecodeExpression):
                self.push(value(identifier))
            else:
                raise RuntimeError("invalid initialiser")

    def block(self, stmt: Block) -> Any:
        #HACK: block creates a function with and immediately executes it
        #      this is because I'm dumb and forgot blocs existed

        self.push_state(stmt.statements)
        bytecode = self.internal_generate(False)
        block = [bt.Frame()] + bytecode + [bt.Raze()]

        self.pop_state()
        self.push(block)

    def function(self, stmt: Function) -> Any:
        name: str = stmt.name.lexeme
        params : list[bt.Identifier] = []
        for param in stmt.params:
            params.append(bt.Identifier(param.lexeme))

        self.push_function(name)

        self.push_state(stmt.body)
        for param in params:
            self.variables[param.value] = BytecodeGeneratorIdentifier(param.value, False)
        bytecodes = self.internal_generate(False)
        bytecodes.append(bt.Return(None))
        # needed to get the actual number of instructions in the function
        # but it is actually wrong at this point and would lead to erroneous jumps
        bytecodes = remove_inner_lists(bytecodes)
        fun = bt.Function(self.get_identifier(name).name, params, len(bytecodes))

        self.pop_state()
        self.push(fun)
        for bytecode in bytecodes:
            self.push(bytecode)

    def return_stmt(self, stmt: Return) -> Any:
        expr = stmt.expr(self)

        if isinstance(expr, Literal):
            if expr.value is None:
                self.push(bt.Return(None))
            else:
                self.push(bt.Return(bt.Value(expr.value)))
            return

        temporary = None
        if isinstance(expr, Variable):
            temporary = self.get_identifier(expr.name.lexeme).name
        elif isinstance(expr, bt.Push):
            #assignment expression
            temporary = expr.identifier
            self.push(expr)
        elif isinstance(expr, BytecodeExpression):
            temporary = self.gen_bytecode_expression(expr)

        self.push(bt.Return(temporary))

    def if_stmt(self, stmt: If) -> Any:
        if_kind = bt.If
        expr = stmt.if_test
        if isinstance(expr, Unary) and is_token(expr.operator, TokenType.MINUS):
            if_kind = bt.IfNotTrue
            expr = expr.right

        name       : str = str(self.next_id()) + 'if'
        temporary  : bt.Identifier = None
        true_block : List[bt.Bytecode] = []
        false_block: List[bt.Bytecode] = []

        expr = expr(self)
        if isinstance(expr, Variable):
            temporary = self.get_identifier(expr.name).name
        elif isinstance(expr, Literal):
            temporary_name = '.tmp' + str(self.next_id())
            temporary   = bt.Identifier(temporary_name)
            create_temp = bt.Create(temporary)
            set_value   = bt.Push(temporary, bt.Value(expr.value))
            self.push(create_temp)
            self.push(set_value)
        elif isinstance(expr, bt.Push):
            #assignment expression
            temporary = expr.identifier
            self.push(expr)
        elif isinstance(expr, BytecodeExpression):
            temporary = self.gen_bytecode_expression(expr)

        if_body = stmt.if_body
        if if_body is not None:
            if isinstance(if_body, Block):
                self.push_state(if_body.statements)
                true_block = self.internal_generate(False)
                self.pop_state()
            else:
                self.push_state([stmt.if_body])
                true_block = self.internal_generate(False)
                self.pop_state()

        if stmt.else_body is not None:
            if isinstance(stmt.else_body, Block):
                else_body: Block = stmt.else_body
                self.push_state(else_body.statements)
                false_block = self.internal_generate(False)
                self.pop_state()
            else:
                self.push_state([stmt.else_body])
                false_block = self.internal_generate(False)
                self.pop_state()

        true_block  = remove_inner_lists(true_block)
        false_block = remove_inner_lists(false_block)
        self.push(if_kind(name, temporary, true_block, false_block))


    def while_stmt(self, stmt: While) -> Any:
        expr = stmt.while_test

        name       : str               = str(self.next_id()) + 'while'
        temporary  : bt.Identifier     = None
        block      : List[bt.Bytecode] = []


        header = None
        expr = expr(self)
        if isinstance(expr, Variable):
            temporary = self.get_identifier(expr.name).name
        elif isinstance(expr, Literal):
            temporary_name = '.tmp' + str(self.next_id())
            temporary   = bt.Identifier(temporary_name)
            create_temp = bt.Create(temporary)
            set_value   = bt.Push(temporary, bt.Value(expr.value))
            self.push(create_temp)
            self.push(set_value)
        elif isinstance(expr, bt.Push):
            #assignment expression
            temporary = expr.identifier
            self.push(expr)
        elif isinstance(expr, BytecodeExpression):
            (header, temporary) = self.gen_internal_bytecode_expression(expr)

        while_body = stmt.while_body
        if isinstance(while_body, Block):
            while_body = while_body.statements
        else:
            while_body = [while_body]

        self.push_state(while_body)
        self.loop_id = name
        block = self.internal_generate(False)
        self.pop_state()

        block  = remove_inner_lists(block)
        self.push(bt.Frame())
        self.push(bt.While(name, header, temporary, block))
        self.push(bt.Raze())

    def break_stmt(self, stmt: Break) -> Any:
        if self.loop_id is None:
            raise RuntimeError('break outside of loop')
        self.push(bt.Jump(bt.Label('.end_' + self.loop_id)))

    def binary(self, expr: Binary) -> Any:
        left = expr.left(self)
        right = expr.right(self)

        binary_bytecode = None
        if expr.operator.token_type == TokenType.STAR:
            if isinstance(left, Literal) and isinstance(right, Literal):
                left.value = left.value * right.value
                return left
            binary_bytecode = bt.Multiplication
        elif expr.operator.token_type == TokenType.SLASH:
            if isinstance(left, Literal) and isinstance(right, Literal):
                left.value = left.value / right.value
                return left
            binary_bytecode = bt.Division
        elif expr.operator.token_type == TokenType.PLUS:
            if isinstance(left, Literal) and isinstance(right, Literal):
                left.value = left.value + right.value
                return left
            binary_bytecode = bt.Addition
        elif expr.operator.token_type == TokenType.MINUS:
            if isinstance(left, Literal) and isinstance(right, Literal):
                left.value = left.value - right.value
                return left
            binary_bytecode = bt.Subtraction
        elif expr.operator.token_type == TokenType.GREATER_EQUAL:
            if isinstance(left, Literal) and isinstance(right, Literal):
                left.value = left.value >= right.value
                return left
            binary_bytecode = bt.GreaterThanEquals
        elif expr.operator.token_type == TokenType.GREATER:
            if isinstance(left, Literal) and isinstance(right, Literal):
                left.value = left.value > right.value
                return left
            binary_bytecode = bt.GreaterThan
        elif expr.operator.token_type == TokenType.LESSER_EQUAL:
            if isinstance(left, Literal) and isinstance(right, Literal):
                left.value = left.value <= right.value
                return left
            binary_bytecode = bt.LessThanEquals
        elif expr.operator.token_type == TokenType.LESSER:
            if isinstance(left, Literal) and isinstance(right, Literal):
                left.value = left.value < right.value
                return left
            binary_bytecode = bt.LessThan
        elif expr.operator.token_type == TokenType.EQUAL_EQUAL:
            if isinstance(left, Literal) and isinstance(right, Literal):
                left.value = left.value == right.value
                return left
            binary_bytecode = bt.Equals
        elif expr.operator.token_type == TokenType.BANG_EQUAL:
            if isinstance(left, Literal) and isinstance(right, Literal):
                left.value = left.value * right.value
                return left
            binary_bytecode = bt.NotEquals
        if binary_bytecode is None:
            raise RuntimeError(f"unsuported unary operator '{expr.operator}'")

        left_val  = bt.Identifier('.tmp' + str(self.next_id()))
        right_val = bt.Identifier('.tmp' + str(self.next_id()))
        if isinstance(left, Variable):
            left_val = self.get_identifier(left.name.lexeme).name
        elif isinstance(left, Literal):
            left_val = bt.Value(left.value)
        else:
            temporary = bt.Create(left_val)
            self.push(temporary)
            if isinstance(left, BytecodeExpression):
                set_value = left(left_val)
                self.push(set_value)

        if isinstance(right, Variable):
            right_val = self.get_identifier(right.name.lexeme).name
        elif isinstance(right, Literal):
            right_val = bt.Value(right.value)
        else:
            temporary = bt.Create(right_val)
            self.push(temporary)
            if isinstance(right, BytecodeExpression):
                set_value = right(right_val)
                self.push(set_value)

        return BytecodeExpression(lambda result:
               binary_bytecode(result, left_val, right_val))

    def unary(self, expr: Unary) -> Any:
        right = expr.right(self)

        unary_bytecode = None
        if is_token(expr.operator, TokenType.MINUS):
            if isinstance(right, Literal):
                right.value = -right.value
                return right
            unary_bytecode = bt.Negate
        elif is_token(expr.operator, TokenType.BANG):
            if isinstance(right, Literal):
                right.value = not right.value
                return right
            unary_bytecode = bt.LogicalNot

        if unary_bytecode is None:
            raise RuntimeError(f"unsupported unary operator '{expr.operator}'")

        temporary_name = '.tmp' + str(self.next_id())
        if isinstance(right, Variable):
            temporary_name = self.get_identifier(right.name.lexeme).name.value
        else:
            temporary = bt.Create(bt.Identifier(temporary_name))
            self.push(temporary)
            if isinstance(right, BytecodeExpression):
                set_value = right(bt.Identifier(temporary_name))
                self.push(set_value)

        return BytecodeExpression(lambda result:
               unary_bytecode(result, bt.Identifier(temporary_name)))

    def literal(self, expr: Literal) -> Any:
        return expr

    def grouping(self, expr: Grouping) -> Any:
        return expr.expr(self)

    def variable(self, expr: Variable) -> Any:
        return expr

    def assignment(self, expr: Assignment) -> Any:
        name  = expr.name.lexeme
        value = expr.initializer(self)
        if isinstance(value, BytecodeExpression):
            temporary = self.gen_bytecode_expression(value)
            return bt.Push(self.get_identifier(name).name, temporary)
        #NOCHEKIN:
        return bt.Push(self.get_identifier(name).name, bt.Value(value.value))

    def call(self, expr: Call) -> Any:
        callee = expr.callee(self)
        if not isinstance(callee, Variable):
            raise RuntimeError("invalid call expression")
        function_name = callee.name.lexeme
        #TODO: make functions have a return type so that we can cascade pseudo typing
        # if not self.get_identifier(function_name).is_function:
        #     raise RuntimeError(f"variable {function_name} does not refer to a function")

        args: list[Any] = []
        for arg in expr.arguments:
            val = arg(self)
            if isinstance(val, Variable):
                name = val.name.lexeme
                if self.get_identifier(name) is not None:
                    args.append(self.get_identifier(name).name)
                else:
                    raise RuntimeError(f"no variable named {name}")
            elif isinstance(val, Literal):
                args.append(bt.Value(val.value))
            elif isinstance(val, BytecodeExpression):
                temporary = self.gen_bytecode_expression(val)
                args.append(temporary)
            else:
                raise RuntimeError("invalid call expression")

        return BytecodeExpression(lambda result:
                bt.Call(result, self.get_identifier(function_name).name, args))

    def array(self, expr: Array) -> Any:
        elements : List[Any] = []
        for elem in expr.elems:
            val = elem(self)
            if isinstance(val, Variable):
                name = val.name.lexeme
                if self.get_identifier(name) is not None:
                    elements.append(self.get_identifier(name).name)
                else:
                    raise RuntimeError(f"no variable named {name}")
            elif isinstance(val, Literal):
                elements.append(bt.Value(val.value))
            elif isinstance(val, BytecodeExpression):
                temporary = self.gen_bytecode_expression(val)
                elements.append(temporary)
            else:
                raise RuntimeError("invalid array")
        return BytecodeExpression(lambda result: bt.Array(result, elements))

    def solve_index(self, expr: Index):
        obj   = expr.indexee(self)
        index = expr.index(self)

        if isinstance(obj, Literal):
            raise RuntimeError('cannot use subscript on literals')

        temporary = None
        if isinstance(obj, Variable):
            name = obj.name.lexeme
            if self.get_identifier(name) is not None:
                temporary = self.get_identifier(name).name
            else:
                raise RuntimeError(f"no variable named {name}")
        elif isinstance(obj, BytecodeExpression):
            temporary = self.gen_bytecode_expression(obj)

        if temporary is None:
            raise RuntimeError('unexpected program state, index temporary was none')

        index_value = None
        if isinstance(index, Variable):
            name = index.name.lexeme
            if self.get_identifier(name) is not None:
                index_value = self.get_identifier(name).name
            else:
                raise RuntimeError(f"no variable named {name}")
        elif isinstance(index, Literal):
            index_value = bt.Value(index.value)
        elif isinstance(index, BytecodeExpression):
            index_value = self.gen_bytecode_expression(index)
        else:
            raise RuntimeError('unexpected program state, index was an unknown type')

        return (temporary, index_value)
    def index(self, expr: Index) -> Any:
        (obj, index) = self.solve_index(expr)

        return BytecodeExpression(lambda result: bt.ArrayGetAtIndex(result, obj, index))

    def indexset(self, expr: IndexSet) -> Any:
        (obj, index) = self.solve_index(expr.index)

        val = expr.value(self)
        value = None
        if isinstance(val, Variable):
            name = val.name.lexeme
            if self.get_identifier(name) is not None:
                value = self.get_identifier(name).name
            else:
                raise RuntimeError(f"no variable named {name}")
        elif isinstance(val, Literal):
            value = bt.Value(val.value)
        elif isinstance(val, BytecodeExpression):
            value = self.gen_bytecode_expression(val)
        else:
            raise RuntimeError("invalid array")

        return BytecodeExpression(lambda result: bt.ArraySetAtIndex(obj, index, value))

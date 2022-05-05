import random
import sys
max_int = sys.maxsize

from src.bytecodes import *
from src.execute import *

def test_addition():
    a = random.randint(0, max_int)
    b = random.randint(0, max_int)
    test_literal_left  = random.randint(0, max_int)
    test_literal_right = random.randint(0, max_int)

    var_a  = Create(Identifier('a'))
    var_b  = Create(Identifier('b'))
    return_var = Create(Identifier('result'))
    set_a  = Push(Identifier('a'), Literal(a))
    set_b  = Push(Identifier('b'), Literal(b))
    init = [var_a, var_b, return_var, set_a, set_b]
    footer = [ Return(Identifier('result')) ]

    add_vars     = Addition(Identifier('result'), Identifier('a'), Identifier('b'))
    add_literal  = Addition(Identifier('result'), Identifier('a'), Literal(test_literal_right))
    add_literals = Addition(Identifier('result'), Literal(test_literal_left), Literal(test_literal_right))
    add_var      = Addition(Identifier('result'), Literal(test_literal_left), Identifier('b'))

    executor = Executor()
    result = executor.execute(init + [add_vars] + footer)
    assert result == a + b
    result = executor.execute(init + [add_literal] + footer)
    assert result == a + test_literal_right
    result = executor.execute(init + [add_literals] + footer)
    assert result == test_literal_left + test_literal_right
    result = executor.execute(init + [add_var] + footer)
    assert result == test_literal_left + b
    
def test_subtraction():
    a = random.randint(0, max_int)
    b = random.randint(0, max_int)
    test_literal_left  = random.randint(0, max_int)
    test_literal_right = random.randint(0, max_int)

    var_a  = Create(Identifier('a'))
    var_b  = Create(Identifier('b'))
    return_var = Create(Identifier('result'))
    set_a  = Push(Identifier('a'), Literal(a))
    set_b  = Push(Identifier('b'), Literal(b))
    init = [var_a, var_b, return_var, set_a, set_b]
    footer = [ Return(Identifier('result')) ]

    add_vars     = Subtraction(Identifier('result'), Identifier('a'), Identifier('b'))
    add_literal  = Subtraction(Identifier('result'), Identifier('a'), Literal(test_literal_right))
    add_literals = Subtraction(Identifier('result'), Literal(test_literal_left), Literal(test_literal_right))
    add_var      = Subtraction(Identifier('result'), Literal(test_literal_left), Identifier('b'))

    executor = Executor()
    result = executor.execute(init + [add_vars] + footer)
    assert result == a - b
    result = executor.execute(init + [add_literal] + footer)
    assert result == a - test_literal_right
    result = executor.execute(init + [add_literals] + footer)
    assert result == test_literal_left - test_literal_right
    result = executor.execute(init + [add_var] + footer)
    assert result == test_literal_left - b

def test_division():
    a = random.randint(0, max_int)
    b = random.randint(0, max_int)
    test_literal_left  = random.randint(0, max_int)
    test_literal_right = random.randint(0, max_int)

    var_a  = Create(Identifier('a'))
    var_b  = Create(Identifier('b'))
    return_var = Create(Identifier('result'))
    set_a  = Push(Identifier('a'), Literal(a))
    set_b  = Push(Identifier('b'), Literal(b))
    init = [var_a, var_b, return_var, set_a, set_b]
    footer = [ Return(Identifier('result')) ]

    add_vars     = Division(Identifier('result'), Identifier('a'), Identifier('b'))
    add_literal  = Division(Identifier('result'), Identifier('a'), Literal(test_literal_right))
    add_literals = Division(Identifier('result'), Literal(test_literal_left), Literal(test_literal_right))
    add_var      = Division(Identifier('result'), Literal(test_literal_left), Identifier('b'))

    executor = Executor()
    result = executor.execute(init + [add_vars] + footer)
    assert result == a / b
    result = executor.execute(init + [add_literal] + footer)
    assert result == a / test_literal_right
    result = executor.execute(init + [add_literals] + footer)
    assert result == test_literal_left / test_literal_right
    result = executor.execute(init + [add_var] + footer)
    assert result == test_literal_left / b

def test_multiplication():
    a = random.randint(0, max_int)
    b = random.randint(0, max_int)
    test_literal_left  = random.randint(0, max_int)
    test_literal_right = random.randint(0, max_int)

    var_a  = Create(Identifier('a'))
    var_b  = Create(Identifier('b'))
    return_var = Create(Identifier('result'))
    set_a  = Push(Identifier('a'), Literal(a))
    set_b  = Push(Identifier('b'), Literal(b))
    init = [var_a, var_b, return_var, set_a, set_b]
    footer = [ Return(Identifier('result')) ]

    add_vars     = Multiplication(Identifier('result'), Identifier('a'), Identifier('b'))
    add_literal  = Multiplication(Identifier('result'), Identifier('a'), Literal(test_literal_right))
    add_literals = Multiplication(Identifier('result'), Literal(test_literal_left), Literal(test_literal_right))
    add_var      = Multiplication(Identifier('result'), Literal(test_literal_left), Identifier('b'))

    executor = Executor()
    result = executor.execute(init + [add_vars] + footer)
    assert result == a * b
    result = executor.execute(init + [add_literal] + footer)
    assert result == a * test_literal_right
    result = executor.execute(init + [add_literals] + footer)
    assert result == test_literal_left * test_literal_right
    result = executor.execute(init + [add_var] + footer)
    assert result == test_literal_left * b




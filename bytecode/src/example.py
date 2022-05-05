from src.bytecode import *
from src.execute import *

def _internal_print(user_data, executor, params):
    result = ''
    for p in params:
        result += str(executor.get(p))
    print(result)
    return

def example_program():
    val_a = Create(Identifier('greg'))
    val_b = Create(Identifier('grog'))
    push_literal    = Push(Identifier('greg'), Literal(55))
    push_identifier = Push(Identifier('greg'), Identifier('greg'))
    add_ii          = Addition(Identifier('grog'), Identifier('greg'), Identifier('greg'))
    add_iv          = Addition(Identifier('grog'), Identifier('greg'), Literal(15))
    add_vv          = Addition(Identifier('grog'), Literal(10), Literal(5))
    add_vi          = Addition(Identifier('grog'), Literal(15), Identifier('greg'))

    funky_dory = Function(Identifier('test_fun'), [], [
        Return(None)
    ])
    fnc = Function(Identifier('add'), 
            [Identifier('a'), Identifier('b')],
            [
                Create(Identifier('result')),
                Addition(Identifier('result'), Identifier('a'), Identifier('b')),
                If('.if_test', Identifier('result'), 
                    [ Return(Identifier('result')) ], 
                    [ Return(Literal(0)) ])
            ])

    funky_call = Call(None, Identifier('test_fun'), [])
    fun_call = Call(Identifier('grog'), Identifier('add'), [
        Identifier('grog'), 
        Identifier('greg')
    ])

    print_greg = Call(None, Identifier('print'), [
        Identifier('greg')
    ])
    print_grog = Call(None, Identifier('print'), [
        Identifier('grog')
    ])
    print_all = Call(None, Identifier('print'), [
        Literal('grog: '), Identifier('grog'),
        Literal(' greg: '), Identifier('greg')
    ])
    print_value = Call(None, Identifier('print'), [
        Literal("hello world!")
    ])

    executor = Executor()
    # TODO: this 
    executor.push('print', None, _internal_print)
    executor.execute([
        print_value,
        funky_dory,
        fnc,
        funky_call,
        val_a, 
        val_b, 
        push_literal, 
        print_greg,
        push_identifier,
        print_greg,
        add_ii, 
        print_grog,
        add_iv, 
        print_grog,
        add_vv, 
        print_grog,
        add_vi,
        print_grog,
        fun_call,
        print_grog,
        print_all
    ])

    print('')
    print(fnc.code)
    for i in range(len(fnc.block)):
        bytecode = fnc.block[i]
        if type(bytecode) == Jump or type(bytecode) == JumpIfTrue:
            print('    ' + str(i) + ': ' + str(bytecode.code) + ' ' + str(bytecode.location))
        else: 
            print('    ' + str(i) + ': ' + str(bytecode.code))

    print(val_a.code)
    print(val_b.code)
    print(push_literal.code)
    print(push_identifier.code)
    print(add_ii.code)
    print(add_iv.code)
    print(add_vv.code)
    print(add_vi.code)



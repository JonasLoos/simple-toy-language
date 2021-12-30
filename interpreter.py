from typing import Any, Callable
from lark.lexer import Token
from lark.tree import Tree

from stdlib import Object, Value, Function, Fail


TODO = ...  # placeholder


class DefinedFunction(Function):
    def __init__(self, name : str, args : list[str], body : list, names : dict[str, Object]):
        def f(*input_args):
            # check if the number of given arguments is correct
            if len(input_args) != len(args):
                raise Fail(f'wrong number of arguments when calling {name}: expected {len(args)}, got {len(input_args)}')
            # initialize arguments
            # only give a copy of `names`, to avoid cluttering the global namespace
            tmp = {**names}
            for arg_name, arg_value in zip(args, input_args):
                tmp[arg_name] = arg_value
            # set `_` to first argument
            tmp['_'] = input_args[0] if len(input_args) > 0 else Value(None)
            # run the function
            return run_body(body, tmp)

        super().__init__(name, f)


def interpret(program : Tree) -> None:
    '''main entry point - interpret the given program '''
    # try to run the program
    try:
        run_program(program)
    # print an error message if it fails
    except Fail as err:
        import sys
        print("fail:", err, file=sys.stderr)


def run_program(program : Tree):
    '''parse the function definitions and run `main`'''
    from stdlib import asdf_print, asdf_input, asdf_add, asdf_sub, asdf_mul, asdf_div, asdf_length
    global_names : dict[str, Object] = {
        'print': Function('print', asdf_print),
        'input': Function('input', asdf_input),
        'add': Function('add', asdf_add),
        'sub': Function('sub', asdf_sub),
        'mul': Function('mul', asdf_mul),
        'div': Function('div', asdf_div),
        'length': Function('length', asdf_length),
    }

    assert program.data == 'program'
    for function_def in program.children:
        assert isinstance(function_def, Tree)
        assert function_def.data == 'function_def'
        name, arguments, *body = function_def.children
        assert isinstance(name, Token)
        assert isinstance(arguments, Tree)
        assert all(isinstance(x, Tree) for x in body)
        args : list[str] = []
        for arg in arguments.children:
            assert isinstance(arg, Token)
            assert arg.type == 'NAME'
            args += arg,
        global_names[name] = DefinedFunction(name, args, body, global_names)

    if 'main' in global_names:
        main = global_names['main']
        if isinstance(main, Function):
            main()
        else:
            raise Fail('main is not a Function')
    else:
        raise Fail('main Function not defined')


def run_body(body : list, names : dict[str, Object]) -> Value:
    '''run the statements in the body of a function or multiline statement'''
    if "_" not in names:
        names["_"] = Value(None)
    for stmt in body:
        if stmt.data == 'line_stmt':
            line_stmt, *_ = stmt.children
            assert len(_) == 0
            assert isinstance(line_stmt, Tree)
            names["_"] = run_line_stmt(line_stmt, names)
        elif stmt.data == 'multiline_stmt':
            multiline_stmt, *stmt_body = stmt.children
            assert len(stmt_body) > 0
            assert isinstance(multiline_stmt, Tree)
            if multiline_stmt.data == 'do_stmt':
                assert all(isinstance(x, Tree) for x in stmt_body)
                names["_body"] = run_body(stmt_body, names)
            else:
                raise Fail(f'unknown multiline_stmt: {multiline_stmt}')
        else:
            raise Fail(f'unknown stmt: {stmt}')
    assert isinstance(names["_"], Value), names['_']  # has to be assured every time `names["_"]` is assigned
    return names["_"]


def run_line_stmt(line_stmt : Tree, names : dict[str, Object]) -> Value:
    '''run a single line statement (includes also parts of a line that could stand alone)'''
    # function call
    if line_stmt.data == 'funccall':
        name, arguments = line_stmt.children
        assert isinstance(name, Token)
        assert isinstance(arguments, Tree)
        assert arguments.data == 'comma_list', arguments.data
        argument_values : list[Value] = []
        for argument in arguments.children:
            assert isinstance(argument, Tree)
            arg, *_ = argument.children
            assert len(_) == 0
            assert isinstance(arg, Tree)
            argument_values += run_line_stmt(arg, names),
        if name in names:
            func = names[name]
            if isinstance(func, Function):
                return func(*argument_values)
            else:
                raise Fail(f'call of {type(func)} object: {name}')
        else:
            raise Fail(f'call of undefined function: {name}')
    # variable assignment
    elif line_stmt.data == 'assignment':
        name, value = line_stmt.children
        assert isinstance(name, Token)
        assert isinstance(value, Tree)
        val, *_ = value.children
        assert len(_) == 0
        assert isinstance(val, Tree)
        names[name] = result = run_line_stmt(val, names)
        return result
    # thing / value
    elif line_stmt.data == 'thing':
        thing, *_ = line_stmt.children
        assert len(_) == 0
        assert isinstance(thing, Token)
        if thing.type == 'NAME':
            if thing in names:
                value = names[thing]
                if isinstance(value, Value):
                    return value
                else:
                    raise Fail(f'use of {type(Value)} object as Value: {thing}')
            else:
                raise Fail(f'use of undefined name: {thing}')
        elif thing.type == "STRING":
            # if it's a format string, format it
            if thing[0] == '"':
                try:
                    return Value(thing[1:-1].format(**get_values(names)))
                except KeyError as err:
                    raise Fail(f'Could not find variable {err} used in format string {thing}')
            # otherwise return just the content
            return Value(thing[1:-1])
        elif thing.type == "LONG_STRING":
            # if it's a format string, format it
            if thing[0] == '"':
                try:
                    return Value(thing[3:-3].format(**get_values(names)))
                except KeyError as err:
                    raise Fail(f'Could not find variable {err} used in format string {thing}')
            # otherwise return just the content
            return Value(thing[3:-3])
        elif thing.type == "DEC_NUMBER":
            return Value(int(thing))
        elif thing.type in ["HEX_NUMBER", "BIN_NUMBER", "OCT_NUMBER", "FLOAT_NUMBER", "IMAG_NUMBER"]:
            raise Fail(f'{thing.type} is not implemented yet')
        else:
            raise Fail(f'unknown thing type: {thing.type}')
    # error
    else:
        # if grammar and interpreter are correct, this point should never be reached
        raise Exception(f'unknown line_stmt: {line_stmt}')



def get_values(names : dict[str, Object]) -> dict[str, Any]:
    '''filter names dict for Values and extract their internal value'''
    return {key: value.value for key, value in names.items() if isinstance(value, Value)}

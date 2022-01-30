'''
provide an `interpret` function for interpreting parsed source code.

author: Jonas Loos (2022)
'''

from typing import Any
from lark.lexer import Token
from lark.tree import Tree
from stdlib import Object, Value, Function, Fail, std_names

TODO = ...  # placeholder



class DefinedFunction(Function):
    '''Function defined in the source code'''
    def __init__(self, name : str, args : list[str], body : Tree, names : dict[str, Object]):
        def fun(*input_args : Value) -> Value:
            '''a callable function created from a given body'''
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

        super().__init__(name, fun)


def interpret(program : Tree) -> None:
    '''main entry point - interpret the given program '''

    # init global namespace
    global_names = {**std_names}

    # parse function definitions
    assert program.data == 'program', program.data
    for function_def in program.children:
        assert isinstance(function_def, Tree), function_def
        assert function_def.data == 'function_def', function_def.data
        name, arguments, body = function_def.children
        assert isinstance(name, Token), name
        assert isinstance(arguments, Tree), arguments
        assert isinstance(body, Tree), body
        args : list[str] = []
        for arg in arguments.children:
            assert isinstance(arg, Token), arg
            assert arg.type == 'NAME', arg.type
            args += arg,
        if name in std_names:
            raise Fail(f'Cannot overwrite a predefined function or value: {name}', name)
        global_names[name] = DefinedFunction(name, args, body, global_names)

    # run main function
    if 'main' in global_names:
        main = global_names['main']
        if isinstance(main, Function):
            main()
        else:
            raise Fail('main is not a Function')
    else:
        raise Fail('main Function not defined')


def run_body(body : Tree, names : dict[str, Object]) -> Value:
    '''run the statements in the body of a function or multiline statement'''
    assert body.data == 'body', body.data
    for stmt in body.children:
        assert isinstance(stmt, Tree), stmt
        # single-line statement
        if stmt.data == 'line_stmt':
            names["_"] = run_line_stmt(stmt, names)
        # multi-line statement
        elif stmt.data == 'multiline_stmt':
            multiline_stmt, = stmt.children
            assert isinstance(multiline_stmt, Tree), multiline_stmt
            match multiline_stmt.data:
                # do
                case 'do_stmt':
                    do_body, = multiline_stmt.children
                    assert isinstance(do_body, Tree), do_body
                    # if block level variable scoope is desired, use `{**names}` instead
                    names["_"] = run_body(do_body, names)
                # if elif... else
                case 'if_stmt':
                    if_condition, if_body, elifs, else_stmt = multiline_stmt.children
                    assert isinstance(if_condition, Tree), if_condition
                    assert if_condition.data == 'line_stmt', if_condition.data
                    assert isinstance(if_body, Tree), if_body
                    assert if_body.data == 'body', if_body.data
                    assert isinstance(elifs, Tree), elifs
                    assert elifs.data == 'elifs', elifs.data
                    assert isinstance(else_stmt, Tree), else_stmt
                    assert else_stmt.data == 'else', else_stmt.data
                    # handle if
                    conditions = [(if_condition, if_body)]
                    # handle elifs
                    for elif_stmt in elifs.children:
                        assert isinstance(elif_stmt, Tree), elif_stmt
                        elif_condition, elif_body = elif_stmt.children
                        assert isinstance(elif_condition, Tree), elif_condition
                        assert isinstance(elif_body, Tree), elif_body
                        conditions += (elif_condition, elif_body),
                    # handle else
                    if len(else_stmt.children) > 0:
                        else_body, = else_stmt.children
                        assert isinstance(else_body, Tree), else_body
                        assert else_body.data == 'body'
                        # use `true` as condition, to make sure else is executed when no other statement is
                        true_stmt = Tree('line_stmt', [Tree('thing', [Token('NAME', 'true')])])  # type: ignore
                        conditions += (true_stmt, else_body),
                    # evaluate all conditions until the correct body to execute is found
                    for condition, stmt_body in conditions:
                        test_result = run_line_stmt(condition, names)
                        if test_result.value:  # use python truthiness
                            names['_'] = run_body(stmt_body, names)
                            break
                # error
                case _:
                    # if grammar and interpreter are correct, this point should never be reached
                    raise Exception(f'unknown multiline_stmt: {multiline_stmt}')
        # error
        else:
            # if grammar and interpreter are correct, this point should never be reached
            raise Exception(f'unknown stmt: {stmt}')
    assert isinstance(names["_"], Value), names['_']  # has to be assured every time `names["_"]` is assigned
    return names["_"]


def run_line_stmt(line_stmt : Tree, names : dict[str, Object]) -> Value:
    '''run a single line statement (includes also parts of a line that could stand alone)'''
    # extract actual statement
    assert line_stmt.data == 'line_stmt', line_stmt.data
    tmp, = line_stmt.children
    assert isinstance(tmp, Tree), tmp
    line_stmt = tmp
    match line_stmt.data:
        # function call
        case 'funccall':
            name, arguments = line_stmt.children
            assert isinstance(name, Token), name
            assert isinstance(arguments, Tree), arguments
            assert arguments.data == 'comma_list', arguments.data
            argument_values : list[Value] = []
            for argument in arguments.children:
                assert isinstance(argument, Tree), argument
                argument_values += run_line_stmt(argument, names),
            if name in names:
                func = names[name]
                if isinstance(func, Function):
                    return func(*argument_values)
                else:
                    raise Fail(f'call of {type(func)} object: {name}', line_stmt)
            else:
                raise Fail(f'call of undefined function: {name}', line_stmt)
        # variable assignment
        case 'assignment':
            name, value = line_stmt.children
            assert isinstance(name, Token), name
            assert name.type == 'NAME', name.type
            assert isinstance(value, Tree), value
            if name in std_names:
                raise Fail(f'Cannot overwrite a predefined function or value: {name}', name)
            names[name] = result = run_line_stmt(value, names)
            return result
        # thing / value
        case 'thing':
            thing, = line_stmt.children
            assert isinstance(thing, Token), thing
            match thing.type:
                case 'NAME':
                    if thing in names:
                        value = names[thing]
                        if isinstance(value, Value):
                            return value
                        else:
                            raise Fail(f'use of {type(Value)} object as Value: {thing}', thing)
                    else:
                        raise Fail(f'use of undefined name: {thing}', thing)
                case "STRING":
                    # if it's a format string, format it
                    if thing[0] == '"':
                        try:
                            return Value(thing[1:-1].format(**get_values(names)))
                        except KeyError as err:
                            raise Fail(f'Could not find variable {err} used in format string {thing}', thing) from err
                    # otherwise return just the content
                    return Value(thing[1:-1])
                case "LONG_STRING":
                    # if it's a format string, format it
                    if thing[0] == '"':
                        try:
                            return Value(thing[3:-3].format(**get_values(names)))
                        except KeyError as err:
                            raise Fail(f'Could not find variable {err} used in format string {thing}', thing) from err
                    # otherwise return just the content
                    return Value(thing[3:-3])
                case "DEC_NUMBER":
                    return Value(int(thing))
                case "HEX_NUMBER" | "BIN_NUMBER" | "OCT_NUMBER" | "FLOAT_NUMBER" | "IMAG_NUMBER":
                    raise Fail(f'{thing.type} is not implemented yet', thing)
                # error
                case _:
                    # if grammar and interpreter are correct, this point should never be reached
                    raise Exception(f'unknown thing type: {thing.type}')
        # error
        case _:
            # if grammar and interpreter are correct, this point should never be reached
            raise Exception(f'unknown line_stmt: {line_stmt}')



def get_values(names : dict[str, Object]) -> dict[str, Any]:
    '''filter names dict for Values and extract their internal value'''
    return {key: value.value for key, value in names.items() if isinstance(value, Value)}

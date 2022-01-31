'''
provide an `interpret` function for interpreting parsed source code.
It uses the Lark.visitors.Interpreter class as a base and is therefore
more concise and extensible, but typing support is limited.

author: Jonas Loos (2022)
'''

# pylint: disable=missing-function-docstring
# pylint: disable=no-self-use

from typing import Any, Callable, TextIO
from lark import Token, Tree
from lark.visitors import Interpreter as LarkInterpreter
import stdlib
from stdlib import Object, Value, Function, Fail, std_names

TODO = ...  # placeholder


class DefinedFunction(Function):
    '''Function defined in the source code'''
    def __call__(self, names : dict[str, Object], *args : Value) -> Object:
        '''TODO remove if Function is adjusted'''
        return self.fun(names, *args)



def interpret(program : Tree, input_steam : TextIO = None, output_stream : TextIO = None) -> None:
    '''main entry point - interpret the given program '''
    # set input and output stream
    if input_steam:
        stdlib.input_stream = input_steam
    if output_stream:
        stdlib.output_stream = output_stream

    # run program
    main = Interpreter().visit(program)
    main()


def wrapStd(f):
    # wrap stdlib functions to accept `names` parameter. TODO: add this to `stdlib.py` and remove here
    return Function(f.name, lambda _, *args: f.fun(*args)) if isinstance(f, Function) else f

class Interpreter(LarkInterpreter):
    '''class for interpreting a program'''

    def program(self, program : Tree) -> Callable:
        # wrap stdlib functions to accept `names` parameter. TODO: add this to `stdlib.py` and remove here
        tmp : dict[str, Object] = {key : wrapStd(f) for key, f in std_names.items()}
        # go through whole program and add global function definitions to global names
        global_names : dict[str, Object] = tmp | dict(self.visit_children(program))
        # run main function
        if 'main' not in global_names:
            raise Fail('main Function not defined')
        main : Object = global_names['main']
        if not isinstance(main, DefinedFunction):
            raise Fail('main is not a Function')
        return lambda: main(global_names)

    def function_def(self, function_def : Tree) -> tuple[str, DefinedFunction]:
        name, arg_names, run_body = self.visit_children(function_def)
        def run_function(names, *args):
            # check if the number of given arguments is correct
            n = len(args)
            if n != len(arg_names):
                raise Fail(f'wrong number of arguments when calling {name}: expected {len(arg_names)}, got {n}')
            # initialize arguments
            # only give a copy of `names`, to avoid cluttering the global namespace
            # set `_` to first argument
            tmp = names | dict(zip(arg_names, args)) | {'_': args[0] if n > 0 else Value(None)}
            return run_body(tmp)
        return name, DefinedFunction(name, run_function)

    def body(self, body : Tree) -> Callable[..., Object]:
        run_stmts = self.visit_children(body)
        def run_body(names : dict[str, Object]) -> Object:
            for run_stmt in run_stmts:
                names['_'] = run_stmt(names)  # `run_stmt` can change `names`
            return names['_']  # type: ignore
        return run_body

    def line_stmt(self, line_stmt : Tree) -> Callable[..., Object]:
        return self.visit_children(line_stmt)[0]

    def multiline_stmt(self, multiline_stmt : Tree) -> Callable[..., Object]:
        return self.visit_children(multiline_stmt)[0]

    def do_stmt(self, do_stmt : Tree) -> Callable[..., Object]:
        def run_do(names : dict[str, Object]) -> Object:
            # if block level variable scoope is desired, use `{**names}`, otherwise use `names`
            return self.visit_children(do_stmt)[0](names)
        return run_do

    def if_stmt(self, if_stmt : Tree) -> Callable[..., Object]:
        if_condition, if_body, elifs, else_stmt = self.visit_children(if_stmt)
        conditions = [(if_condition, if_body), *elifs]
        def run_if(names : dict[str, Object]) -> Object:
            for condition, stmt_body in conditions:
                test_result = condition(names)
                if test_result.value:  # use python truthiness
                    return stmt_body(names)
            return else_stmt(names)
        return run_if

    def elifs(self, elifs : Tree) -> list[tuple[Callable,Callable]]:
        return self.visit_children(elifs)

    def elif_stmt(self, elif_stmt : Tree) -> tuple[Callable,Callable]:
        elif_condition, elif_body = self.visit_children(elif_stmt)
        return elif_condition, elif_body

    def else_stmt(self, else_stmt : Tree) -> Callable[..., Object]:
        tmp = self.visit_children(else_stmt)
        return tmp[0] if tmp else lambda _: Value(None)

    def funccall(self, funccall : Tree) -> Callable[..., Object]:
        name, arguments = self.visit_children(funccall)
        def run_funccall(names : dict[str, Object]) -> Object:
            if name not in names:
                raise Fail(f'call of undefined function: {name}', funccall)
            func = names[name]
            if not isinstance(func, Function):
                raise Fail(f'call of {type(func)} object: {name}', funccall)
            # evaluate arguments
            args = [x(names) for x in arguments]
            # call the function
            return func(names, *args)  # TODO: adjust Function class in `stdlib.py`
        return run_funccall

    def comma_list(self, comma_list : Tree) -> list[Callable]:
        return self.visit_children(comma_list)

    def assignment(self, assignment : Tree) -> Callable[..., Object]:
        name, run_value = self.visit_children(assignment)
        def run_assignment(names : dict[str, Object]) -> Object:
            if name in std_names:
                raise Fail(f'Cannot overwrite a predefined function or value `{name}`', assignment)
            result = names[name] = run_value(names)
            return result
        return run_assignment

    def thing(self, thing : Tree) -> Callable[..., Object]:
        value, = thing.children
        assert isinstance(value, Token)
        def run_thing(names : dict[str, Object]) -> Object:
            match value.type:
                case 'NAME':
                    if value not in names:
                        raise Fail(f'Use of undefined name `{value}`', value)
                    return names[value]
                case "STRING":
                    # if it's a format string, format it
                    if value[0] == '"':
                        try:
                            return Value(value[1:-1].format(**get_values(names)))
                        except KeyError as err:
                            raise Fail(f'Could not find variable {err} used in format string {value}', value) from err
                    # otherwise return just the content
                    return Value(value[1:-1])
                case "LONG_STRING":
                    # if it's a format string, format it
                    if value[0] == '"':
                        try:
                            return Value(value[3:-3].format(**get_values(names)))
                        except KeyError as err:
                            raise Fail(f'Could not find variable {err} used in format string {value}', value) from err
                    # otherwise return just the content
                    return Value(value[3:-3])
                case "DEC_NUMBER":
                    return Value(int(value))
                case "HEX_NUMBER" | "BIN_NUMBER" | "OCT_NUMBER" | "FLOAT_NUMBER" | "IMAG_NUMBER":
                    raise Fail(f'{value.type} is not implemented yet', value)
                # error
                case _:
                    # if grammar and interpreter are correct, this point should never be reached
                    raise Exception(f'unknown thing type: {value.type}')
        return run_thing


def get_values(names : dict[str, Object]) -> dict[str, Any]:
    '''filter names dict for Values and extract their internal value'''
    return {key: value.value for key, value in names.items() if isinstance(value, Value)}

'''
provide an `interpret` function for interpreting parsed source code.
It uses the Lark.visitors.Interpreter class as a base and is therefore
quite concise, but typing support is limited.

author: Jonas Loos (2022)
'''

# pylint: disable=missing-function-docstring
# pylint: disable=no-self-use

from typing import Any, Callable
from lark import Token, Tree
from lark.visitors import Interpreter as LarkInterpreter
from stdlib import Object, Value, Function, Fail, std_names

TODO = ...  # placeholder


class DefinedFunction(Function):
    '''Function defined in the source code'''
    def __init__(self, name : str, args : list[str], run_body : Callable):
        def fun(names : dict[str, Object], *input_args : Value) -> Value:
            '''a callable function created from a given body'''
            # check if the number of given arguments is correct
            if len(input_args) != len(args):
                raise Fail(f'wrong number of arguments when calling {name}: expected {len(args)}, got {len(input_args)}')
            # initialize arguments
            # only give a copy of `names`, to avoid cluttering the global namespace
            # set `_` to first argument
            tmp = names | dict(zip(args, input_args)) | {'_': input_args[0] if len(input_args) > 0 else Value(None)}
            # run the function
            return run_body(tmp)

        super().__init__(name, fun)

    def __call__(self, names : dict[str, Object], *args : Value):
        '''TODO remove if Function is adjusted'''
        print('calling function', self.name, 'with', args, 'and names:', names)
        self.fun(names, *args)



def interpret(program : Tree) -> None:
    '''main entry point - interpret the given program '''
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
        name, arguments, run_body = self.visit_children(function_def)
        return name, DefinedFunction(name, arguments, run_body)

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
            # evaluate arguments and call the function
            return func(names, *[x(names) for x in arguments])  # TODO: adjust Function class in `stdlib.py`
        return run_funccall

    def comma_list(self, comma_list : Tree) -> list[Callable]:
        return self.visit_children(comma_list)

    def assignment(self, assignment : Tree) -> Callable[..., Object]:
        name, run_value = self.visit_children(assignment)
        def run_assignment(names : dict[str, Object]) -> Object:
            if name in std_names:
                raise Fail(f'Cannot overwrite a predefined function or value: {name}', assignment)
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
                        raise Fail(f'use of undefined name: {value}', value)
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

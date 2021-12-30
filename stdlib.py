from typing import Any, Callable, Union

from lark.lexer import Token
from lark.tree import Tree

TODO = ...  # placeholder



##########
########## basic objects
##########

class Object:
    """abstract base class for all objects"""
    pass

class Value(Object):
    def __init__(self, value):
        self.value = value

class Function(Object):
    def __init__(self, name : str, f : Callable):
        self.name = name
        self.f = f
    
    def __call__(self, *args: Value) -> Value:
        # print('calling function', self.name)
        return self.f(*args)


##########
########## Fail during execution
##########

class Fail(Exception):
    """wrapper class to symbolize errors caused by the interpreted source code"""

    source : Union[list[str], None] = None

    def __init__(self, msg : Any, item : Union[Tree, Token] = None):
        if item:
            # get first and last token
            first = last = item
            while not isinstance(first, Token):
                assert isinstance(first, Tree)
                first = first.children[0]
            while not isinstance(last, Token):
                assert isinstance(last, Tree)
                last = last.children[-1]
            # only continue if first and last tokens were found
            if first and last:
                # get start- and endpoints of the error
                firstline = first.line
                lastline = last.end_line
                firstcolumn = first.column
                lastcolumn = last.end_column
                # only continue if valid start- and endpoints were found
                if firstline != None and lastline != None and firstcolumn != None and lastcolumn != None:
                    # create error message
                    text = ''
                    # single line error
                    if firstline == lastline:
                        text += f'error in line {firstline}\n'
                        if self.source:
                            text += f'{firstline:4d} | {self.source[firstline-1]}\n'
                            indent = firstcolumn + 2 + max(4, len(str(firstline)))
                            col_err_len = lastcolumn - firstcolumn
                            text += ' ' * indent + '^' * col_err_len + '\n'
                    # error over multiple lines
                    else:
                        text += f'error in lines {firstline} - {lastline}\n'
                        if self.source:
                            for i in range(firstline, lastline+1):
                                text += f'{firstline:4d} | {self.source[firstline]}\n'
                    # create the actual exception
                    super().__init__(text + msg)
                    return

        # default error message without line information
        super().__init__("error: " + msg)



##########
########## basic functions
##########

# the `asdf_`-prefix is important for avoiding name conflicts with python functions

def asdf_print(*args : Value) -> Value:
    print(*[x.value for x in args])
    return args[0]  # return *first* argument

def asdf_input() -> Value:
    return Value(input())

def asdf_add(*args : Value) -> Value:
    if len(args) < 2:
        raise Fail(f'add: need at least two arguments, got {len(args)}')
    try:
        return Value(sum(arg.value for arg in args))
    except Exception as err:
        raise Fail(err)

def asdf_sub(*args : Value) -> Value:
    if len(args) < 2:
        raise Fail(f'sub: need at least two arguments, got {len(args)}')
    try:
        return Value(args[0].value - sum(arg.value for arg in args[1:]))
    except Exception as err:
        raise Fail(err)

def asdf_mul(*args : Value) -> Value:
    if len(args) < 2:
        raise Fail(f'mul: need at least two arguments, got {len(args)}')
    try:
        import math
        return Value(math.prod(arg.value for arg in args))
    except Exception as err:
        raise Fail(err)

def asdf_div(*args : Value) -> Value:
    if len(args) < 2:
        raise Fail(f'div: need at least two arguments, got {len(args)}')
    try:
        import math
        return Value(args[0].value / math.prod(arg.value for arg in args[1:]))
    except Exception as err:
        raise Fail(err)

def asdf_length(x : Value) -> Value:
    if hasattr(x.value, '__len__'):
        return Value(len(x.value))
    else:
        raise Fail(f'cannot determine length of {x}')

def asdf_eq(a : Value, b : Value) -> Value:
    try:
        return Value(a.value == b.value)
    except TypeError:
        raise Fail(f'`eq` between {type(a.value)} and {type(b.value)} is not supported')

def asdf_lt(a : Value, b : Value) -> Value:
    try:
        return Value(a.value < b.value)
    except TypeError:
        raise Fail(f'`lt` between {type(a.value)} and {type(b.value)} is not supported')

def asdf_leq(a : Value, b : Value) -> Value:
    try:
        return Value(a.value <= b.value)
    except TypeError:
        raise Fail(f'l`leq` between {type(a.value)} and {type(b.value)} is not supported')

def asdf_gt(a : Value, b : Value) -> Value:
    try:
        return Value(a.value > b.value)
    except TypeError:
        raise Fail(f'`gt` between {type(a.value)} and {type(b.value)} is not supported')

def asdf_geq(a : Value, b : Value) -> Value:
    try:
        return Value(a.value >= b.value)
    except TypeError:
        raise Fail(f'g`geq` between {type(a.value)} and {type(b.value)} is not supported')


std_names : dict[str, Object] = {
    'print': Function('print', asdf_print),
    'input': Function('input', asdf_input),
    'add': Function('add', asdf_add),
    'sub': Function('sub', asdf_sub),
    'mul': Function('mul', asdf_mul),
    'div': Function('div', asdf_div),
    'length': Function('length', asdf_length),
    'eq': Function('eq', asdf_eq),
    'lt': Function('lt', asdf_lt),
    'leq': Function('leq', asdf_leq),
    'gt': Function('gt', asdf_gt),
    'geq': Function('geq', asdf_geq),
    'true': Value(True),
    'false': Value(False),
    '_': Value(None),
}

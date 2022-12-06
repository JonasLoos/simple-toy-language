'''
This class contains the implementations of the functions in the standard-library.

author: Jonas Loos (2022)
'''

import sys
from typing import Any, Callable
from lark.lexer import Token
from lark.tree import Tree

TODO = ...  # placeholder

# define default input/output streams
input_stream = sys.stdin
output_stream = sys.stdout


##########
########## basic objects
##########

class Object:
    """abstract base class for all objects"""


class Value(Object):
    '''basic value object'''
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'Value({self.value})'

    def print(self):
        '''determine how this object should be printed out'''
        return self.value


class Function(Object):
    '''basic function object'''
    def __init__(self, name : str, fun : Callable):
        self.name = name
        self.fun = fun

    def __repr__(self):
        return f'Function({self.name}, {self.fun})'

    def __call__(self, namespace, *args: Value) -> Value:
        return self.fun(namespace, *args)

    def print(self):
        '''determine how this object should be printed out'''
        return f'<Function {self.name}>'

class StdFunction(Function):
    '''a function which is part of the standard lib'''
    def __init__(self, name : str, fun : Callable):
        # ignore the global namespace of the program, as the standard-lib functions don't need it
        super().__init__(name, lambda namespace, *args: fun(*args))



##########
########## Fail during execution
##########

class Fail(Exception):
    """wrapper class to symbolize errors caused by the interpreted source code"""

    source : list[str] = []

    @classmethod
    def init_class(cls, source_text):
        '''initialize the Fail class using the source code'''
        cls.source = source_text.split('\n')

    def __init__(self, msg : Any, item : Tree | Token | None = None):
        if item:
            # get first and last token
            first = last = item
            while not isinstance(first, Token):
                assert isinstance(first, Tree)
                first = first.children[0]
            while not isinstance(last, Token):
                assert isinstance(last, Tree)
                last = last.children[-1]  # TODO: what if there are not children?
            # only continue if first and last tokens were found
            if first and last:
                # get start- and endpoints of the error
                firstline = first.line
                lastline = last.end_line
                firstcolumn = first.column
                lastcolumn = last.end_column
                # only continue if valid start- and endpoints were found
                if firstline is not None and lastline is not None and firstcolumn is not None and lastcolumn is not None:
                    indent = '  '
                    prev_lines = 1
                    # create error message
                    text = '\nError during execution:\n\n'
                    if self.source:
                        start = max(firstline - prev_lines, 1)
                        # print lines
                        for linenumber in range(start, lastline+1):
                            text += indent + f'{linenumber:4d} | {self.source[linenumber-1]}\n'
                        # print column indicators
                        if firstline == lastline:
                            col_err_indent = firstcolumn + 2 + max(4, len(str(firstline)))
                            col_err_len = lastcolumn - firstcolumn
                            text += indent + ' ' * col_err_indent + '^' * col_err_len + '\n\n'
                        text += '\n'
                    # add error message and line information
                    text += '\n'.join(indent + x for x in msg.split('\n'))
                    text += ', at line' + (f' {firstline}' if firstline == lastline else f's {firstline}-{lastline}')
                    # create the actual exception
                    super().__init__(text)
                    return

        # default error message without line information
        super().__init__("Error during execution: " + str(msg))



##########
########## basic functions
##########

# the `asdf_`-prefix is important for avoiding name conflicts with python functions

def asdf_print(*args : Value) -> Value:
    '''print the given values'''
    print(*[x.print() for x in args], file=output_stream)
    return args[0]  # return *first* argument

def asdf_input() -> Value:
    '''read and return user input'''
    # ignore the newline symbol at the end
    return Value(input_stream.readline()[:-1])

def asdf_add(*args : Value) -> Value:
    '''operation: add'''
    if len(args) < 2:
        raise Fail(f'add: need at least two arguments, got {len(args)}')
    try:
        return Value(sum(arg.value for arg in args))
    except TypeError as err:
        raise Fail(err) from err

def asdf_sub(*args : Value) -> Value:
    '''operation: subtract'''
    if len(args) < 2:
        raise Fail(f'sub: need at least two arguments, got {len(args)}')
    try:
        return Value(args[0].value - sum(arg.value for arg in args[1:]))
    except TypeError as err:
        raise Fail(err) from err

def asdf_mul(*args : Value) -> Value:
    '''operation: multiply'''
    if len(args) < 2:
        raise Fail(f'mul: need at least two arguments, got {len(args)}')
    try:
        import math
        return Value(math.prod(arg.value for arg in args))
    except TypeError as err:
        raise Fail(err) from err

def asdf_div(*args : Value) -> Value:
    '''operation: divide'''
    if len(args) < 2:
        raise Fail(f'div: need at least two arguments, got {len(args)}')
    try:
        import math
        return Value(args[0].value / math.prod(arg.value for arg in args[1:]))
    except ZeroDivisionError as err:
        raise Fail('div: disors have to be greater than 0') from err
    except TypeError as err:
        raise Fail(err) from err

def asdf_length(x : Value) -> Value:
    '''determine length'''
    if hasattr(x.value, '__len__'):
        return Value(len(x.value))
    else:
        raise Fail(f'cannot determine length of {x}')

def asdf_eq(a : Value, b : Value) -> Value:
    '''comparison: equal'''
    try:
        return Value(a.value == b.value)
    except TypeError as err:
        raise Fail(f'`eq` between {type(a.value)} and {type(b.value)} is not supported') from err

def asdf_lt(a : Value, b : Value) -> Value:
    '''comparison: greater than'''
    try:
        return Value(a.value < b.value)
    except TypeError as err:
        raise Fail(f'`lt` between {type(a.value)} and {type(b.value)} is not supported') from err

def asdf_leq(a : Value, b : Value) -> Value:
    '''comparison: less equal'''
    try:
        return Value(a.value <= b.value)
    except TypeError as err:
        raise Fail(f'`leq` between {type(a.value)} and {type(b.value)} is not supported') from err

def asdf_gt(a : Value, b : Value) -> Value:
    '''comparison: greater than'''
    try:
        return Value(a.value > b.value)
    except TypeError as err:
        raise Fail(f'`gt` between {type(a.value)} and {type(b.value)} is not supported') from err

def asdf_geq(a : Value, b : Value) -> Value:
    '''comparison: greater equal'''
    try:
        return Value(a.value >= b.value)
    except TypeError as err:
        raise Fail(f'`geq` between {type(a.value)} and {type(b.value)} is not supported') from err



std_names : dict[str, Object] = {
    'print': StdFunction('print', asdf_print),
    'input': StdFunction('input', asdf_input),
    'add': StdFunction('add', asdf_add),
    'sub': StdFunction('sub', asdf_sub),
    'mul': StdFunction('mul', asdf_mul),
    'div': StdFunction('div', asdf_div),
    'length': StdFunction('length', asdf_length),
    'eq': StdFunction('eq', asdf_eq),
    'lt': StdFunction('lt', asdf_lt),
    'leq': StdFunction('leq', asdf_leq),
    'gt': StdFunction('gt', asdf_gt),
    'geq': StdFunction('geq', asdf_geq),
    'true': Value(True),
    'false': Value(False),
    '_': Value(None),
}

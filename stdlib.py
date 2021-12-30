from typing import Callable


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



class Fail(Exception):
    """wrapper class to symbolize errors caused by the interpreted source code"""
    pass




def asdf_print(*args : Value) -> Value:
    print(*[x.value for x in args])
    return args[0]  # return *first* argument

def asdf_add(*args : Value) -> Value:
    if len(args) < 2:
        raise Fail('add: need at least two arguments')
    try:
        return Value(sum(arg.value for arg in args))
    except Exception as err:
        raise Fail(err)

def asdf_sub(*args : Value) -> Value:
    if len(args) < 2:
        raise Fail('sub: need at least two arguments')
    try:
        return Value(args[0].value - sum(arg.value for arg in args[1:]))
    except Exception as err:
        raise Fail(err)

def asdf_mul(*args : Value) -> Value:
    if len(args) < 2:
        raise Fail('mul: need at least two arguments')
    try:
        import math
        return Value(math.prod(arg.value for arg in args))
    except Exception as err:
        raise Fail(err)

def asdf_div(*args : Value) -> Value:
    if len(args) < 2:
        raise Fail('div: need at least two arguments')
    try:
        import math
        return Value(args[0].value / math.prod(arg.value for arg in args[1:]))
    except Exception as err:
        raise Fail(err)

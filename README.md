# a simple toy programming language

[![Pylint](https://github.com/JonasLoos/simple-toy-language/workflows/Pylint/badge.svg?branch=main)](https://github.com/JonasLoos/simple-toy-language/actions/workflows/pylint.yml)
[![Unittest](https://github.com/JonasLoos/simple-toy-language/workflows/Unittest/badge.svg?branch=main)](https://github.com/JonasLoos/simple-toy-language/actions/workflows/unittest.yml)

This is a parser and interpreter for a new simple toy language. It is implemented in Python `3.11` with the help of [lark](https://github.com/lark-parser/lark).

usage:

```
python main.py examples/input.asdf
```


## Example

```rb
# comments start with `#` and go until the end of the line
def main()  # the main function is called when the program is run
    # indentation matters
    print('what is your name?')  # print a string
    name = input()  # read a line from stdin and save it in `name`
    make_greeting(name)  # call a function
    print(_)  # use `_` to get the result of the previous line

def make_greeting(x)  # functions can be defined with `def name(args...)\n body...`
    if lt(length(x), 42)  # `lt` is less than
        "Hello, {x}!"  # inside double quotes, variables can be used with `{variable}`
    else
        'This does not seem like a name.'  # inside single quotes, no variables can be used
    # the result of the last expression is returned
```


## Features

* functions with a fixed number of arguments: `def name(args...)\n body...`
* assignments: `name = value`
* basic mathematical operations: `add`, `sub`, `mul`, `div`
* IO operations: `input`, `print`
* string operations: `length`, `"format string with {variable}."`
* control-flow statements: `if ...\n ... elif ...\n else ...` and comparison operators
* use `_` to get the result of the previous line
* (sometimes) nice error messages


## Development

This project uses `pylint` with a corresponding github action for automatic code analysis.

Unit-tests can be found in `test.py`.

The easiest way to get started is to use VS Code with the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension and `Rebuild and Reopen in Container`.


## How it works

When calling `python main.py examples/input.asdf`, `main.py` checks the arguments, opens the program `input.asdf`, feeds it into the `parse` function from `parsing.py` and the result into the `interpret` function from `interpreter.py`.

In `parse`, the lark earley parser is used with the grammar from `grammar.lark` to turn the program text into a abstract syntax tree (AST).

This AST is then interpreted by the `interpret` function, i.e. the program is run. The interpreter first evaluates all function definitions and then executes the `main` function. Thereby, it follows the control flow statements and function calls and evaluates the expressions - all by calling the corresponding functions of the `Interpreter` class from `interpreter.py`.

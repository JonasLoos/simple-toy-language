# a simple toy programming language

[![Pylint](https://github.com/JonasLoos/simple-toy-language/workflows/Pylint/badge.svg?branch=main)](https://github.com/JonasLoos/simple-toy-language/actions/workflows/pylint.yml)
[![Unittest](https://github.com/JonasLoos/simple-toy-language/workflows/Unittest/badge.svg?branch=main)](https://github.com/JonasLoos/simple-toy-language/actions/workflows/unittest.yml)

This is a parser and interpreter for a new simple toy language. It is implemented in Python `3.10` with the help of [lark](https://github.com/lark-parser/lark).

usage:

```sh
python main.py input.asdf
```


## Features

* functions with a fixed number of arguments: `def name(args...)\n body...`
* assignments: `name = value`
* basic mathematical operations: `add`, `sub`, `mul`, `div`
* IO operations: `input`, `print`
* string operations: `length`, `"format string with {variable}."`
* control-flow statements: `if ...\n ... elif ...\n else ...`
* use `_` to get the result of the previous line
* (sometimes) nice error messages


## Development

This project uses `pylint` with a corresponding github action for automatic code analysis.

Unit-tests can be found in `test.py`.

The easiest way to get started is to use VS Code with the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension and `Rebuild and Reopen in Container`.

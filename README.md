# a simple toy programming language

This is a parser and interpreter for a new simple toy language. It is implemented in Python `3.10` with the help of [lark](https://github.com/lark-parser/lark).

usage:

```sh
python main.py input.asdf
```

features:
* functions with a fixed number of arguments: `def name(args...)\n body...`
* assignments: `name = value`
* basic mathematical operations: `add`, `sub`, `mul`, `div`
* IO operations: `input`, `print`
* string operations: `length`, `"format string with {variable}."`
* control-flow statements: `if ...\n ... elif ...\n else ...`
* use `_` to get the result of the previous line
* (sometimes) nice error messages

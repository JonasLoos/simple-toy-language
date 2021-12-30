# a simple toy programming language

This is an interpreter for a new simple toy language. It is implemented in Python with the help of [lark](https://github.com/lark-parser/lark).

usage:

```sh
python main.py input.asdf
```

features:
* functions with a fixed number of arguments: `def name(args...)\n body...`
* assignments: `name = value`
* basic mathematical operations: `add`, `sub`, `mul`, `div`
* print operation: `print`
* multiline statements: `do`
* use `_` to get the result of the previous operation

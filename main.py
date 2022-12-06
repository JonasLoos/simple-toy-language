'''
main file of simple-toy-language

author: Jonas Loos (2022)
'''

import sys

from parsing import ParserError, parse  # pylint: disable=deprecated-module
from stdlib import Fail as InterpreterError
from interpreter import interpret



def fail(msg):
    '''print error message and exit'''
    print(msg, file=sys.stderr)
    sys.exit(1)


def main() -> None:
    '''parse and interpret the source code file specified as a command line argument'''
    # check command line args
    if len(sys.argv) != 2:
        fail(f'USAGE: {sys.argv[0]} FILE')

    # open source code file
    with open(sys.argv[1], encoding='utf-8') as input_file:
        input_text = input_file.read()

    # init error class
    InterpreterError.init_class(input_text)

    # debug
    # print(parse(input_text).pretty())
    # print('-'*50)

    # run parser and interpreter
    try:
        interpret(parse(input_text))
    except (ParserError, InterpreterError) as error:
        fail(error)



if __name__ == '__main__':
    main()

'''
main file of simple-toy-language

author: Jonas Loos (2022)
'''

import sys
from stdlib import Fail
from interpreter import interpret
from parser import parse


def main() -> None:
    '''parse and interpret the source code file specified as a command line argument'''
    # check command line args
    if len(sys.argv) != 2:
        print(f'USAGE: {sys.argv[0]} FILE')
        exit()

    # open source code file
    with open(sys.argv[1]) as input_file:
        input_text = input_file.read()

    # init error class
    Fail.init_class(input_text)

    # debug
    # print(parse(input_text).pretty())
    # print('-'*50)

    # run interpreter
    interpret(parse(input_text))



if __name__ == '__main__':
    main()

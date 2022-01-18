import sys
from lark.exceptions import UnexpectedToken
from lark import Lark
from lark.indenter import Indenter
from lark.tree import Tree


class TreeIndenter(Indenter):
    NL_type : str = '_NEWLINE'
    OPEN_PAREN_types : list = []
    CLOSE_PAREN_types : list = []
    INDENT_type : str = '_INDENT'
    DEDENT_type : str = '_DEDENT'
    tab_len : int = 8


def main() -> None:
    if len(sys.argv) != 2:
        print(f'USAGE: {sys.argv[0]} FILE')
        exit()
    with open(sys.argv[1]) as input_file:
        input_text = input_file.read()

    # debug
    # print(parse(input_text).pretty())
    # print('-'*50)

    # init error class
    from stdlib import Fail
    Fail.source = input_text.split('\n')

    # run interpreter
    from interpreter import interpret
    interpret(parse(input_text))



def parse(input_text : str) -> Tree:
    # dont fail when no newline at the end
    input_text += '\n'

    # parse and print
    try:
        return parser.parse(input_text)
    except UnexpectedToken as error:
        indent = '\n    '
        nl = '\n'
        res = ''
        def pos(x : int) -> int: return x if x > 0 else 0
        res = f'{indent}{indent.join([f"{i:2d}| {x}" for i, x in enumerate(str(input_text).split(nl)[pos(error.line-2):error.line], pos(error.line-1))])}'  # source code
        res += indent + '   ' + ' ' * error.column + '^\n'  # column indicator
        if error: res += (f'{indent}{indent.join(str(error).strip().split(nl))}')
        raise Exception(res + '\n') from error


# init parser (even if imported)
with open('grammar.lark') as grammar_file:
    # fast but limited
    # parser = Lark(grammar_file, parser='lalr', postlex=TreeIndenter())  # type: ignore[abstract]
    # slower but can handle more
    parser = Lark(grammar_file, parser='earley', postlex=TreeIndenter())  # type: ignore[abstract]



if __name__ == '__main__':
    main()

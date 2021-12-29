from lark.exceptions import UnexpectedToken
from lark import Lark
from lark.indenter import Indenter
import sys


class TreeIndenter(Indenter):
    NL_type : str = '_NEWLINE'
    OPEN_PAREN_types : list = []
    CLOSE_PAREN_types : list = []
    INDENT_type : str = '_INDENT'
    DEDENT_type : str = '_DEDENT'
    tab_len : int = 8


def main(input_text : str) -> str:
    # dont fail when no newline at the end
    input_text += '\n'
    
    # parse and print
    try:
        return parser.parse(input_text).pretty()
    except UnexpectedToken as error:
        indent = '\n    '
        nl = '\n'
        res = ''
        def pos(x : int) -> int: return x if x > 0 else 0
        res = f'{indent}{indent.join([f"{i:2d}| {x}" for i, x in enumerate(str(input_text).split(nl)[pos(error.line-2):error.line], pos(error.line-1))])}'  # source code
        res += indent + '   ' + ' ' * error.column + '^\n'  # column indicator
        if error: res += (f'{indent}{indent.join(str(error).strip().split(nl))}')
        raise Exception(res + '\n')


# init parser (even if imported)
# fast but limited
# parser = Lark(open('grammar.lark'), parser='lalr', postlex=TreeIndenter())  # type: ignore[abstract]
# slower but can handle more
parser = Lark(open('grammar.lark'), parser='earley', postlex=TreeIndenter())  # type: ignore[abstract]



if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'USAGE: {sys.argv[0]} FILE')
        exit()
    input_text = open(sys.argv[1]).read()
    try:
        print(main(input_text))
    except Exception as e:
        print(e)

'''
initialize a the parser and provide the `parse` function

author: Jonas Loos (2022)
'''

from lark.indenter import Indenter
from lark import Lark, LexError, ParseError
from lark.tree import Tree


class TreeIndenter(Indenter):
    NL_type : str = '_NEWLINE'
    OPEN_PAREN_types : list = []
    CLOSE_PAREN_types : list = []
    INDENT_type : str = '_INDENT'
    DEDENT_type : str = '_DEDENT'
    tab_len : int = 8



def parse(input_text : str) -> Tree:
    '''parse a given string of source code'''
    # dont fail when there is no newline at the end
    input_text += '\n'

    # parse and print
    try:
        return parser.parse(input_text)
    except (LexError, ParseError) as error:
        indent = '\n  '
        # create error message
        res = 'Error during parsing:\n'
        if hasattr(error, 'line'):
            error_lines = str(input_text).split('\n')[max(0, error.line-2):error.line]  # select relevant lines from source code
            error_lines = [f'{i:4d} | {x}' for i, x in enumerate(error_lines, max(0, error.line-1))]  # indent relevant lines
            res += f'{indent}{indent.join(error_lines)}'  # add relevant lines
        if hasattr(error, 'column'):
            res += indent + '      ' + ' ' * error.column + '^\n'  # add column indicator
        res += indent + indent.join(str(error).strip().split('\n'))  # add error message
        # print error
        print(res)
        exit()
        # raise Exception(res + '\n') from error  # use this instead if the traceback should be shown


# init parser (even if imported)
with open('grammar.lark') as grammar_file:
    # fast but limited
    # parser = Lark(grammar_file, parser='lalr', postlex=TreeIndenter())  # type: ignore[abstract]
    # slower but can handle more
    parser = Lark(grammar_file, parser='earley', postlex=TreeIndenter())  # type: ignore[abstract]

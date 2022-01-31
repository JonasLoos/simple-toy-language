'''
do some unit-tests

author: Jonas Loos (2022)
'''

# pylint: disable=missing-function-docstring

import unittest
import io
import subprocess
import textwrap
import parser  # pylint: disable=deprecated-module
import interpreterLark as interpreter
from stdlib import Fail



class TestMain(unittest.TestCase):
    '''unit-tests for main.py'''
    @staticmethod
    def run_main(*args : str):
        return subprocess.run(['python', 'main.py', *args], capture_output=True, check=False)

    def test_no_args(self):
        result = self.run_main()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stderr, b'USAGE: main.py FILE\n')

    def test_non_source_code_file(self):
        result = self.run_main('test.py')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stderr.decode()[:5], 'Error')


class TestParser(unittest.TestCase):
    '''unit-tests for parser.py'''
    def test_empty(self):
        with self.assertRaises(parser.ParserError):
            parser.parse('')

    def test_only_comments(self):
        with self.assertRaises(parser.ParserError):
            parser.parse('''\
                # comment
            ''')

    def test_simple_def(self):
        try:
            parser.parse('''\
                def test()
                    42
            ''')
        except parser.ParserError as err:
            self.fail(f"test failed: unexpected ParserError: {err}")


class TestInterpreter(unittest.TestCase):
    '''unit-tests for interpreter.py'''
    def assertOutputEqual(self, program : str, test : str):
        try:
            with io.StringIO() as result:
                interpreter.interpret(parser.parse(textwrap.dedent(program)), output_stream=result)
                self.assertEqual(result.getvalue(), test)
        except (parser.ParseError, Fail) as err:
            self.fail(f"test failed: unexpected Error: {err}")

    def test_print42(self):
        self.assertOutputEqual('''\
            def main()
                print('42')
        ''', '42\n')

    def test_fun_call(self):
        self.assertOutputEqual('''\
            def main()
                print(f(21))
            def f(x)
                mul(x, 2)
        ''', '42\n')


if __name__ == '__main__':
    unittest.main()

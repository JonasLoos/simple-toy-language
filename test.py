'''
do some unit-tests

author: Jonas Loos (2022)
'''

# pylint: disable=missing-function-docstring

import unittest
import io
import subprocess
import textwrap
from parsing import parse, ParserError
from interpreter import interpret
from stdlib import Fail



def run_file(filename : str, input_text : bytes = b''):
    return subprocess.run(['python', 'main.py', filename], input=input_text, capture_output=True, check=False)


class TestMain(unittest.TestCase):
    '''unit-tests for main.py'''

    def test_no_args(self):
        result = subprocess.run(['python', 'main.py'], capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stderr.strip(), b'USAGE: python main.py FILE')

    def test_many_args(self):
        result = subprocess.run(['python', 'main.py', 'asdf', 'asdf'], capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stderr.strip(), b'USAGE: python main.py FILE')

    def test_non_existing_file(self):
        result = run_file('asdfasdfasdf')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stderr.strip(), b'File not found: asdfasdfasdf')

    def test_non_source_code_file(self):
        result = run_file('test.py')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stderr.decode()[:5], 'Error')


class TestParser(unittest.TestCase):
    '''unit-tests for parser.py'''

    def test_empty(self):
        with self.assertRaises(ParserError):
            parse('')

    def test_only_comments(self):
        with self.assertRaises(ParserError):
            parse('''\
                # comment
            ''')

    def test_simple_def(self):
        try:
            parse('''\
                def test()
                    42
            ''')
        except ParserError as err:
            self.fail(f"test failed: unexpected ParserError: {err}")


class TestInterpreter(unittest.TestCase):
    '''unit-tests for interpreter.py'''

    def assertOutputEqual(self, program : str, test : str):
        '''test if the output when running the `program` is equal to `test`'''
        try:
            with io.StringIO() as result:
                interpret(parse(textwrap.dedent(program)), output_stream=result)
                self.assertEqual(result.getvalue(), test)
        except (ParserError, Fail) as err:
            self.fail(f"test failed: unexpected Error: {err}")

    def assertFail(self, program, msg : str = ''):
        '''test if execution of `program` fails and optionally if `msg` is part of the error message'''
        try:
            with io.StringIO() as result:
                interpret(parse(textwrap.dedent(program)), output_stream=result)
                self.fail('test failed: no error was thrown')
        except Fail as err:
            if msg:
                self.assertIn(msg, str(err))

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

    def test_assignment(self):
        self.assertOutputEqual('''\
            def main()
                x = 42
                y = x
                print(y)
        ''', '42\n')

    def test_format_string(self):
        self.assertOutputEqual('''\
            def main()
                x = 42
                print("the answer is {x}")
        ''', 'the answer is 42\n')

    def test_missing_function_def(self):
        self.assertFail('''\
            def main()
                undefinedfun(42)
        ''', 'call of undefined function')

    def test_while(self):
        self.assertOutputEqual('''\
            def main()
                x = 0
                while lt(x, 10)
                    x = add(x, 1)
                print(x)
        ''', '10\n')


class TestExamles(unittest.TestCase):
    '''unit-tests for examples'''

    def test_counter(self):
        result = run_file('examples/counter.asdf')
        self.assertEqual(result.returncode, 0)

    def test_factorial(self):
        result = run_file('examples/factorial.asdf', b'10')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), b'factorial(10) = 3628800')

    def test_fox(self):
        result = run_file('examples/fox.asdf', b'asdf\n')
        self.assertEqual(result.returncode, 0)
        print(result.stdout.decode().replace('\r\n','\n'))
        self.assertEqual(result.stdout.decode().replace('\r\n','\n'), 'Please answer the question: \'What does the fox say?\'\nYour answer is `asdf`. It is 4 characters long.\nThank you for your opinion on that matter.\n')

    def test_greet(self):
        result = run_file('examples/greet.asdf', b'World\n')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip()[-13:], b'Hello, World!')

if __name__ == '__main__':
    unittest.main()

'''
do some unit-tests

author: Jonas Loos (2022)
'''

# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long

import unittest

import subprocess
import parser  # pylint: disable=deprecated-module


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




if __name__ == '__main__':
    unittest.main()

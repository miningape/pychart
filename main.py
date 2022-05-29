import sys
from os.path import dirname
sys.path.append(dirname(__file__))

import argparse
from src.pychart.runner import run_prompt, run_file, run_file_as_bytecode, run_as_bytecode, run

def main():
    parser = argparse.ArgumentParser(prog='pychart')
    parser.add_argument('file', nargs='?', help='run a pychart file')
    parser.add_argument('--version', '-V', action='store_true')
    parser.add_argument('--bytecode', '-b', action='store_true')
    parser.add_argument('--print_bytecode', '-print', action='store_true')
    parser.add_argument('-run', nargs='?', help='run pychart source')


    kwargs = vars(parser.parse_args())
    if kwargs.get('run'):
        if kwargs.get('bytecode'):
            should_print = kwargs.get('print_bytecode')
            run_as_bytecode(kwargs.pop('run'), should_print)
        else:
            run(kwargs.pop('run'))
    elif kwargs.get('file'):
        if kwargs.get('bytecode'):
            should_print = kwargs.get('print_bytecode')
            run_file_as_bytecode(kwargs.pop('file'), should_print)
        else:
            run_file(kwargs.pop('file'))
    else:
        run_prompt()


if __name__ == '__main__':
    main()

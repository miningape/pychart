from . import __version__

import argparse
from .runner import run_prompt, run_file, run_bytecode

def main():
    parser = argparse.ArgumentParser(prog='pychart')
    parser.add_argument('file', nargs='?', help='run a pychart file')
    parser.add_argument('--version', '-V', action='store_true')
    parser.add_argument('--bytecode', '-b', action='store_true')
    parser.add_argument('--print_bytecode', '-print', action='store_true')

    kwargs = vars(parser.parse_args())
    if kwargs.pop('version'):
        print(f'v{__version__}')
    elif kwargs.get('bytecode'):
        should_print = kwargs.get('print_bytecode')
        run_bytecode(kwargs.pop('file'), should_print)
    elif kwargs.get('file'):
        run_file(kwargs.pop('file'))
    else:
        run_prompt()


if __name__ == '__main__':
    main()

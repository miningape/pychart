from . import __version__

import argparse
from .runner import run_prompt, run_file

def main():
    parser = argparse.ArgumentParser(prog='pychart')
    parser.add_argument('file', nargs='?', help='run a pychart file')
    parser.add_argument('--version', '-V', action='store_true')

    kwargs = vars(parser.parse_args())
    if kwargs.pop('version'):
        print(f'v{__version__}')
    elif kwargs.get('file'):
        run_file(kwargs.pop('file'))
    else:
        run_prompt()
        

if __name__ == '__main__':
    main()

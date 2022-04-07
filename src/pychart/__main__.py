from . import __version__

import argparse
from .runner import run_prompt, run_file

def main():
    """
    The default entrypoint for the pychart-lang 

    usage: pychart [-h] [--version] [file]

    positional arguments:
      file           run a pychart file

    optional arguments:
      -h, --help     show this help message and exit
      --version, -V
    """
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

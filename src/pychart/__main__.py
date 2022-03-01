import argparse
from .runner import run_prompt, run_file

def main():
    parser = argparse.ArgumentParser(prog='pychart')
    parser.add_argument('--run', '-r', help='run a pychart file')

    kwargs = vars(parser.parse_args())
    if kwargs.get('run'):
        run_file(kwargs.pop('run'))
    else:
        run_prompt()




if __name__ == '__main__':
    main()
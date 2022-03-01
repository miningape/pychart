import argparse
from .runner import run_prompt, run_file

def main():
    parser = argparse.ArgumentParser(prog='pychart')
    parser.add_argument('file', help='run a pychart file')

    kwargs = vars(parser.parse_args())
    if kwargs.get('file'):
        run_file(kwargs.pop('file'))
    else:
        run_prompt()




if __name__ == '__main__':
    main()

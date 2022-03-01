

class Handler():
    def handle_error(self, error):
        print('handling error', end='\n\t')
        for line in error.traceback:
            print(line, end='\n\t')
            print(type(line), end='\n\t')

handler = Handler()
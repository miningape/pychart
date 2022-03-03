

class BaseError(Exception):
    def __init__(self, message):
        super().__init__(message)

    @property
    def traceback(self):
        return self._traceback


class SyntaxError(BaseError):
    def __init__(self, message, tokens, current):
        self.tokens = tokens
        self.current = current
        super().__init__(message)
    
    def __str__(self):
        string = ''
        current_token = self.tokens[self.current]
        current_line = current_token.line

        start_of_line = self.current
        while self.tokens[start_of_line].line == current_line:
            start_of_line -= 1

        start_of_line += 1

        end_of_line = self.current
        while self.tokens[end_of_line].line == current_line:
            end_of_line += 1


        for token in self.tokens[start_of_line:end_of_line]:
            if token == current_token:
                string += '~~'
            string += token.lexem + ' '

            if token == current_token:
                string += '~~'

        return string

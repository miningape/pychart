

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
        while start_of_line > 0 and self.tokens[start_of_line].line == current_line:
            start_of_line -= 1

        end_of_line = self.current
        while end_of_line < len(self.tokens) and self.tokens[end_of_line].line == current_line:
            end_of_line += 1


        for token, index in zip(self.tokens[start_of_line:end_of_line], range(start_of_line, end_of_line)):
            if index == self.current:
                string += '~~ '
            string += token.lexeme + ' '

            if index == self.current:
                string += '~~'

        return string

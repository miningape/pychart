from .handler import handler
from abc import ABCMeta, abstractmethod
import traceback

class BaseError(Exception):
    def __init__(self, message):
        self._traceback = traceback .format_stack()

        super().__init__(message)

    @property
    def traceback(self):
        return self._traceback


class SyntaxError(BaseError):
    pass

class TypeError(BaseError):
    pass

from abc import ABCMeta, abstractmethod


class BaseError(Exception):
    pass


class SyntaxError(BaseError):
    pass
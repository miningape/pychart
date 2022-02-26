from abc import ABCMeta, abstractmethod
from enum import Enum


class Error(metaclass=ABCMeta):
    pass


class ErrorCodeEnum(Enum):
    pass
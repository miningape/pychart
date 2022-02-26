from abc import ABCMeta, abstractmethod
from enum import enum


class Error(metaclass=ABCMeta):
    pass


class ErrorCodeEnum(Enum):
    pass
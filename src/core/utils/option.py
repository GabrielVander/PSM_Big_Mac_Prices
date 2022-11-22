from __future__ import annotations

import abc
import typing

_T = typing.TypeVar('_T')


class Option(typing.Generic[_T], abc.ABC):
    @staticmethod
    def some(value: _T) -> Some[_T]:
        return Some[_T](value)

    @staticmethod
    def empty() -> Empty[_T]:
        return Empty()

    @abc.abstractmethod
    def is_some(self) -> bool:
        pass  # pragma: nocover

    @abc.abstractmethod
    def is_empty(self) -> bool:
        pass  # pragma: nocover


class Some(Option[_T]):
    _value: _T

    def __init__(self, value: _T) -> None:
        self._value = value

    @property
    def value(self) -> _T:
        return self._value

    def is_some(self) -> bool:
        return True

    def is_empty(self) -> bool:
        return False


class Empty(Option[_T]):

    def is_some(self) -> bool:
        return False

    def is_empty(self) -> bool:
        return True

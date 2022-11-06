from __future__ import annotations

import abc
import typing

OkT = typing.TypeVar('OkT')
ErrT = typing.TypeVar('ErrT')


class Result(typing.Generic[OkT, ErrT], abc.ABC):

    @staticmethod
    def ok(ok_value: OkT) -> Ok[OkT, ErrT]:
        return Ok[OkT, ErrT](ok_value)

    @staticmethod
    def error(err_value: ErrT) -> Error[OkT, ErrT]:
        return Error[OkT, ErrT](err_value)

    @abc.abstractmethod
    def is_ok(self) -> bool:
        pass  # pragma: nocover

    @abc.abstractmethod
    def is_err(self) -> bool:
        pass  # pragma: nocover


class Ok(Result, typing.Generic[OkT, ErrT]):
    _value: OkT

    def __init__(self, value: OkT) -> None:
        self._value = value

    @property
    def value(self) -> OkT:
        return self._value

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False


class Error(Result, typing.Generic[OkT, ErrT]):
    _value: ErrT

    def __init__(self, value: ErrT) -> None:
        self._value = value

    @property
    def value(self) -> ErrT:
        return self._value

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

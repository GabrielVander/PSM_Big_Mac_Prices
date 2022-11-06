from __future__ import annotations

import abc
import dataclasses
import pathlib
import typing

import pandas  # type: ignore

from src.core.utils.result import Result


class CsvFileReader:

    @staticmethod
    async def read(path: pathlib.Path) -> Result[CsvFileOutput, CsvFileReaderFailure]:
        is_not_a_file: bool = not path.is_file()
        does_not_exist: bool = not path.exists()
        has_file_error: bool = is_not_a_file or does_not_exist

        if has_file_error:
            if is_not_a_file:
                return Result.error(CsvFileReaderNotAFileFailure(details='Given file path is not a file'))

            return Result.error(CsvFileReaderNotAFileFailure(details='Given file path does not exist'))

        pandas_data_frame: pandas.DataFrame = pandas.read_csv(path)
        output: CsvFileOutput = pandas_data_frame.to_dict(orient='index')

        return Result.ok(output)


@dataclasses.dataclass(frozen=True, kw_only=True)
class CsvFileReaderFailure(abc.ABC):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class CsvFileReaderNotAFileFailure(CsvFileReaderFailure):
    details: str


CsvCellType: typing.TypeAlias = str | int | float
CsvFileOutput: typing.TypeAlias = dict[int, dict[str, CsvCellType]]

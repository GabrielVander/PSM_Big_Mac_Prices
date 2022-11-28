from __future__ import annotations

import abc
import dataclasses
import pathlib
import typing

from src.core.utils.result import Error, Ok, Result
from src.features.price_loading.data.data_sources.models.csv_price_model import CsvPriceModel
from src.features.price_loading.data.data_sources.utils.csv_file_reader import (
    CsvFileOutput,
    CsvFileReader,
    CsvFileReaderFailure,
    CsvFileReaderNonExistingFileFailure, CsvFileReaderNotAFileFailure,
)


class CsvDataSource:
    _csv_file_path: pathlib.Path
    _csv_file_reader: CsvFileReader

    def __init__(self, csv_file_path: pathlib.Path, csv_file_reader: CsvFileReader) -> None:
        self._csv_file_path = csv_file_path
        self._csv_file_reader = csv_file_reader

    async def load(self) -> Result[list[CsvPriceModel], CsvDataSourceFailure]:
        try:
            file_contents: CsvFileOutput = await self._load_csv_file()
            models: list[CsvPriceModel] = self._to_models(file_contents)

            return Result.ok(models)
        except (_ReaderNotAFileFailure, _ReaderNonExistingFileFailure) as reader_file_failure:
            return Result.error(CsvDataSourceDependenciesFailure(reason=reader_file_failure.details))
        except _ReaderGenericFailure:
            return Result.error(CsvDataSourceDependenciesFailure(reason='Unexpected csv file reader failure'))

    async def _load_csv_file(self) -> CsvFileOutput:
        file_result: Result[CsvFileOutput, CsvFileReaderFailure] = await self._csv_file_reader.read(self._csv_file_path)

        if file_result.is_err():
            err_result: Error[CsvFileOutput, CsvFileReaderFailure] = typing.cast(Error, file_result)
            failure: CsvFileReaderFailure = err_result.value

            if isinstance(failure, CsvFileReaderNotAFileFailure):
                not_a_file_failure: CsvFileReaderNotAFileFailure = typing.cast(CsvFileReaderNotAFileFailure, failure)

                raise _ReaderNotAFileFailure(not_a_file_failure.details)
            if isinstance(failure, CsvFileReaderNonExistingFileFailure):
                non_existing_file_failure: CsvFileReaderNonExistingFileFailure = typing.cast(
                    CsvFileReaderNonExistingFileFailure,
                    failure
                )

                raise _ReaderNonExistingFileFailure(non_existing_file_failure.details)

            raise _ReaderGenericFailure()

        file_ok_result: Ok[CsvFileOutput, CsvFileReaderFailure] = typing.cast(Ok, file_result)

        return file_ok_result.value

    def _to_models(self, file_contents: CsvFileOutput) -> list[CsvPriceModel]:
        return [self._to_model(p) for p in file_contents.values()]

    @staticmethod
    def _to_model(raw_price: dict[str, str | int | float]) -> CsvPriceModel:
        date_key: str = 'date      '
        currency_code_key: str = 'currency_code'
        name_key: str = 'name              '
        local_price: str = 'local_price'
        dollar_exchange_key: str = 'dollar_ex'
        dollar_price_key: str = 'dollar_price'

        return CsvPriceModel(
            date=typing.cast(str, raw_price[date_key]),
            currency_code=typing.cast(str, raw_price[currency_code_key]),
            name=typing.cast(str, raw_price[name_key]),
            local_price=float(raw_price[local_price]),
            dollar_ex=float(raw_price[dollar_exchange_key]),
            dollar_price=float(raw_price[dollar_price_key]),
        )


class _ReaderGenericFailure(Exception):
    pass


class _ReaderNotAFileFailure(Exception):
    details: str

    def __init__(self, details: str) -> None:
        self.details = details
        super().__init__()


class _ReaderNonExistingFileFailure(Exception):
    details: str

    def __init__(self, details: str) -> None:
        self.details = details
        super().__init__()


@dataclasses.dataclass(frozen=True, kw_only=True)
class CsvDataSourceFailure(abc.ABC):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class CsvDataSourceDependenciesFailure(CsvDataSourceFailure):
    reason: str

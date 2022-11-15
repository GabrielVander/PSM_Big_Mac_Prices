import dataclasses
import pathlib
import typing
from collections.abc import Generator

import decoy
import pytest

from src.core.data.data_sources.csv_data_source import (
    CsvDataSource,
    CsvDataSourceDependenciesFailure,
    CsvDataSourceFailure,
)
from src.core.data.data_sources.models.csv_price_model import CsvPriceModel
from src.core.data.data_sources.utils.csv_file_reader import (
    CsvFileOutput,
    CsvFileReader,
    CsvFileReaderFailure,
    CsvFileReaderNonExistingFileFailure, CsvFileReaderNotAFileFailure,
)
from src.core.utils.result import Error, Ok, Result


@dataclasses.dataclass(frozen=True, kw_only=True)
class _CsvFileReaderUnexpectedFailure(CsvFileReaderFailure):
    pass


class TestCsvDataSource:
    _decoy: decoy.Decoy
    _dummy_csv_reader: CsvFileReader
    _dummy_csv_file_path: pathlib.Path
    _data_source: CsvDataSource

    @pytest.fixture(autouse=True)
    def set_up_and_tear_down(self) -> Generator[None, None, None]:
        # Set Up
        self._decoy = decoy.Decoy()
        self._dummy_csv_reader = self._decoy.mock(cls=CsvFileReader)
        self._dummy_csv_file_path = self._decoy.mock(cls=pathlib.Path)
        self._data_source = CsvDataSource(
            csv_file_path=self._dummy_csv_file_path,
            csv_file_reader=self._dummy_csv_reader
        )

        yield

        # Tear Down
        self._decoy.reset()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'dict_output, expected_entries',
        [
            ({}, []),
            ({
                 0: {
                     'date      ':         '2000-04-01',
                     'currency_code':      'ARS',
                     'name              ': 'Argentina',
                     'local_price':        '2.5',
                     'dollar_ex':          '1',
                     'dollar_price':       '2.5',
                 }
             }, [
                 CsvPriceModel(
                     date='2000-04-01',
                     currency_code='ARS',
                     name='Argentina',
                     local_price=2.5,
                     dollar_ex=1.0,
                     dollar_price=2.5,
                 )
             ]),
            ({
                 0: {
                     'date      ':         '2000-04-01',
                     'currency_code':      'ARS',
                     'name              ': 'Argentina',
                     'local_price':        '2.5',
                     'dollar_ex':          '1',
                     'dollar_price':       '2.5',
                 },
                 1: {
                     'date      ':         'GBg',
                     'currency_code':      '072wj3S',
                     'name              ': 'Ly09',
                     'local_price':        '447.00',
                     'dollar_ex':          '895.12',
                     'dollar_price':       '406.19',
                 },
                 2: {
                     'date      ':         'lEfU',
                     'currency_code':      'feY',
                     'name              ': 'MZ6269aS',
                     'local_price':        '666.78',
                     'dollar_ex':          '838.51',
                     'dollar_price':       '760.49',
                 }
             }, [
                 CsvPriceModel(
                     date='2000-04-01',
                     currency_code='ARS',
                     name='Argentina',
                     local_price=2.5,
                     dollar_ex=1.0,
                     dollar_price=2.5,
                 ),
                 CsvPriceModel(
                     date='GBg',
                     currency_code='072wj3S',
                     name='Ly09',
                     local_price=447.00,
                     dollar_ex=895.12,
                     dollar_price=406.19,
                 ),
                 CsvPriceModel(
                     date='lEfU',
                     currency_code='feY',
                     name='MZ6269aS',
                     local_price=666.78,
                     dollar_ex=838.51,
                     dollar_price=760.49,
                 )
             ]),
        ]
    )
    async def test_load_should_map_dict_output_correctly(
        self,
        dict_output: CsvFileOutput,
        expected_entries: list[CsvPriceModel]
    ) -> None:
        self._decoy.when(
            await self._dummy_csv_reader.read(path=self._dummy_csv_file_path)
        ).then_return(Result.ok(dict_output))

        result: Result[list[CsvPriceModel], CsvDataSourceFailure] = await self._data_source.load()

        assert result.is_ok()
        ok_result: Ok[list[CsvPriceModel], CsvDataSourceFailure] = typing.cast(Ok, result)
        models: list[CsvPriceModel] = ok_result.value

        assert models == expected_entries

    # noinspection SpellCheckingInspection
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'reader_failure, expected_reason',
        [
            (CsvFileReaderNotAFileFailure(details=''), ''),
            (CsvFileReaderNotAFileFailure(details='GNUaldJ'), 'GNUaldJ'),
            (CsvFileReaderNonExistingFileFailure(details=''), ''),
            (CsvFileReaderNonExistingFileFailure(details='65ZVn'), '65ZVn'),
            (_CsvFileReaderUnexpectedFailure(), 'Unexpected csv file reader failure'),
        ]
    )
    async def test_should_return_dependencies_failure(
        self,
        reader_failure: CsvFileReaderFailure,
        expected_reason: str,
    ) -> None:
        self._decoy.when(
            await self._dummy_csv_reader.read(path=self._dummy_csv_file_path)
        ).then_return(Result.error(reader_failure))

        result: Result[list[CsvPriceModel], CsvDataSourceFailure] = await self._data_source.load()

        assert result.is_err()
        err_result: Error[list[CsvPriceModel], CsvDataSourceFailure] = typing.cast(Error, result)
        failure: CsvDataSourceFailure = err_result.value

        assert failure == CsvDataSourceDependenciesFailure(reason=expected_reason)

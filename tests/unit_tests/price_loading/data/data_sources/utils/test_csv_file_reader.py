import pathlib
import typing
from collections.abc import Callable, Generator

import decoy
import pandas  # type: ignore
import pytest

from src.core.utils.result import Error, Ok, Result
from src.features.price_loading.data.data_sources.utils.csv_file_reader import (
    CsvFileOutput,
    CsvFileReader,
    CsvFileReaderFailure,
    CsvFileReaderNonExistingFileFailure, CsvFileReaderNotAFileFailure,
)


class TestCsvFileReader:
    _decoy: decoy.Decoy
    _reader: CsvFileReader

    @pytest.fixture(autouse=True)
    def set_up_and_tear_down(self) -> Generator[None, None, None]:
        # Set Up
        self._decoy = decoy.Decoy()
        self._reader = CsvFileReader()

        yield

        # Tear Down
        self._decoy.reset()

    @pytest.mark.asyncio
    async def test_should_return_file_failure_if_path_is_not_a_file(self) -> None:
        dummy_path: pathlib.Path = self._decoy.mock(cls=pathlib.Path)

        self._decoy.when(
            dummy_path.is_file()
        ).then_return(False)

        result: Result[CsvFileOutput, CsvFileReaderFailure] = await self._reader.read(dummy_path)

        assert result.is_err()
        err_result: Error[CsvFileOutput, CsvFileReaderFailure] = typing.cast(Error, result)
        failure: CsvFileReaderFailure = err_result.value

        assert isinstance(failure, CsvFileReaderNotAFileFailure)
        not_a_file_failure: CsvFileReaderNotAFileFailure = typing.cast(CsvFileReaderNotAFileFailure, failure)

        assert not_a_file_failure.details == 'Given file path is not a file'

    @pytest.mark.asyncio
    async def test_should_return_file_failure_if_path_does_not_exist(self) -> None:
        dummy_path: pathlib.Path = self._decoy.mock(cls=pathlib.Path)

        self._decoy.when(
            dummy_path.is_file()
        ).then_return(True)

        self._decoy.when(
            dummy_path.exists()
        ).then_return(False)

        result: Result[CsvFileOutput, CsvFileReaderFailure] = await self._reader.read(dummy_path)

        assert result.is_err()
        err_result: Error[CsvFileOutput, CsvFileReaderFailure] = typing.cast(Error, result)
        failure: CsvFileReaderFailure = err_result.value

        assert isinstance(failure, CsvFileReaderNonExistingFileFailure)
        non_existing_file_failure: CsvFileReaderNonExistingFileFailure = typing.cast(
            CsvFileReaderNonExistingFileFailure,
            failure
        )

        assert non_existing_file_failure.details == 'Given file path does not exist'

    @pytest.mark.asyncio
    async def test_should_use_pandas_correctly(self, monkeypatch: pytest.MonkeyPatch) -> None:
        dummy_path: pathlib.Path = self._decoy.mock(cls=pathlib.Path)
        dummy_data_frame: pandas.DataFrame = self._decoy.mock(cls=pandas.DataFrame)
        dummy_dict_output: CsvFileOutput = self._decoy.mock(cls=CsvFileOutput)
        dummy_pandas_reader: Callable[[pathlib.Path], pandas.DataFrame] = self._decoy.mock(func=pandas.read_csv)

        self._decoy.when(
            dummy_path.is_file()
        ).then_return(True)

        self._decoy.when(
            dummy_path.exists()
        ).then_return(True)

        self._decoy.when(
            dummy_pandas_reader(dummy_path)
        ).then_return(dummy_data_frame)

        self._decoy.when(
            dummy_data_frame.to_dict(orient='index')
        ).then_return(dummy_dict_output)

        monkeypatch.setattr(pandas, 'read_csv', dummy_pandas_reader)

        result: Result[CsvFileOutput, CsvFileReaderFailure] = await self._reader.read(dummy_path)

        assert result.is_ok()
        ok_result: Ok[CsvFileOutput, CsvFileReaderFailure] = typing.cast(Ok, result)
        output: CsvFileOutput = ok_result.value

        assert output is dummy_dict_output

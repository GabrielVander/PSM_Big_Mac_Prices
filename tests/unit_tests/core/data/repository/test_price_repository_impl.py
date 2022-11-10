import typing
from collections.abc import Callable, Generator

import decoy
import pytest

from src.core.data.data_sources.csv_data_source import (
    CsvDataSource,
    CsvDataSourceDependenciesFailure,
    CsvDataSourceFailure,
)
from src.core.data.data_sources.models.csv_price_model import CsvPriceModel
from src.core.data.repositories.mappers.csv_price_mapper import CsvPriceMapper, CsvPriceMapperFailure
from src.core.data.repositories.price_repository_impl import PriceRepositoryImpl
from src.core.domain.entities.price_entry import PriceEntry
from src.core.domain.repository.price_repository import (
    PriceRepositoryDependenciesFailure,
    PriceRepositoryFailure,
    PriceRepositoryGenericFailure,
)
from src.core.utils.result import Error, Ok, Result


class TestPriceRepositoryImpl:
    _decoy: decoy.Decoy
    _dummy_csv_data_source: CsvDataSource
    _dummy_csv_price_model_mapper: CsvPriceMapper
    _repository: PriceRepositoryImpl

    @pytest.fixture(autouse=True)
    def set_up_and_tear_down(self) -> Generator[None, None, None]:
        # Set Up
        self._decoy = decoy.Decoy()
        self._dummy_csv_data_source = self._decoy.mock(cls=CsvDataSource)
        self._dummy_csv_price_model_mapper = self._decoy.mock(cls=CsvPriceMapper)
        self._repository = PriceRepositoryImpl(
            csv_data_source=self._dummy_csv_data_source,
            csv_price_model_mapper=self._dummy_csv_price_model_mapper
        )

        yield

        # Tear Down
        self._decoy.reset()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'amount_of_entries',
        [
            0,
            1,
            3,
            999,
        ]
    )
    async def test_fetch_should_return_ok(self, amount_of_entries: int) -> None:
        models: list[CsvPriceModel] = [self._decoy.mock(cls=CsvPriceModel) for _ in range(amount_of_entries)]
        expected_entities: list[PriceEntry] = [self._decoy.mock(cls=PriceEntry) for _ in models]

        self._decoy.when(
            await self._dummy_csv_data_source.load()
        ).then_return(Result.ok(models))

        self._decoy.when(
            self._dummy_csv_price_model_mapper.map(decoy.matchers.Anything())
        ).then_return(*map(lambda e: Result.ok(e), expected_entities))

        result: Result[list[PriceEntry], PriceRepositoryFailure] = await self._repository.fetch()

        assert result.is_ok()

        ok_result: Ok = typing.cast(Ok, result)
        actual_entities: list[PriceEntry] = ok_result.value

        assert actual_entities == expected_entities

        self._decoy.verify(
            await self._dummy_csv_data_source.load(),
            times=1
        )

        self._decoy.verify(
            self._dummy_csv_price_model_mapper.map(decoy.matchers.IsA(CsvPriceModel)),
            times=amount_of_entries
        )

    @pytest.mark.asyncio
    async def test_fetch_should_return_generic_failure_if_data_source_failure(self) -> None:
        data_source_failure: CsvDataSourceFailure = self._decoy.mock(cls=CsvDataSourceFailure)

        self._decoy.when(
            await self._dummy_csv_data_source.load()
        ).then_return(Result.error(data_source_failure))

        result: Result[list[PriceEntry], PriceRepositoryFailure] = await self._repository.fetch()

        assert result.is_err()

        err_result: Error[list[PriceEntry], PriceRepositoryFailure] = typing.cast(Error, result)
        failure: PriceRepositoryFailure = err_result.value

        assert failure == PriceRepositoryGenericFailure()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'amount_of_entries, indexes_with_defect',
        [
            (1, (0,)),
            (2, (0,)),
            (2, (0, 1)),
            (3, (0,)),
            (3, (1,)),
            (3, (2,)),
            (3, (0, 1, 2)),
        ]
    )
    async def test_fetch_should_filter_models_if_mapper_failure(
        self,
        amount_of_entries: int,
        indexes_with_defect: tuple[int]
    ) -> None:
        assert indexes_with_defect
        assert len(indexes_with_defect) <= amount_of_entries
        assert max(indexes_with_defect) < amount_of_entries
        assert min(indexes_with_defect) >= 0

        def map_models(
            raw_models: list[CsvPriceModel],
            indexes_with_failure: tuple[int],
            failure_builder: Callable[[], CsvPriceMapperFailure],
            entity_builder: Callable[[], PriceEntry],
        ) -> list[PriceEntry | CsvPriceMapperFailure]:
            entries: list[PriceEntry | CsvPriceMapperFailure] = []

            for i, m in enumerate(raw_models):
                if i in indexes_with_failure:
                    entries.append(failure_builder())
                    continue

                entries.append(entity_builder())

            return entries

        models: list[CsvPriceModel] = [self._decoy.mock(cls=CsvPriceModel) for _ in range(amount_of_entries)]
        mapped_models: list[PriceEntry | CsvPriceMapperFailure] = map_models(
            raw_models=models,
            indexes_with_failure=indexes_with_defect,
            failure_builder=lambda: self._decoy.mock(cls=CsvPriceMapperFailure),
            entity_builder=lambda: self._decoy.mock(cls=PriceEntry),
        )

        expected_entities: list[PriceEntry] = [m for m in mapped_models if isinstance(m, PriceEntry)]

        self._decoy.when(
            await self._dummy_csv_data_source.load()
        ).then_return(Result.ok(models))

        self._decoy.when(
            self._dummy_csv_price_model_mapper.map(decoy.matchers.Anything())
        ).then_return(
            *map(
                lambda e: Result.error(e) if isinstance(e, CsvPriceMapperFailure) else Result.ok(e),
                mapped_models
            )
        )

        result: Result[list[PriceEntry], PriceRepositoryFailure] = await self._repository.fetch()

        assert result.is_ok()

        ok_result: Ok[list[PriceEntry], PriceRepositoryFailure] = typing.cast(Ok, result)
        actual_entities: list[PriceEntry] = ok_result.value

        assert len(actual_entities) == amount_of_entries - len(indexes_with_defect)
        assert actual_entities == expected_entities

        self._decoy.verify(
            await self._dummy_csv_data_source.load(),
            times=1
        )

        self._decoy.verify(
            self._dummy_csv_price_model_mapper.map(decoy.matchers.IsA(CsvPriceModel)),
            times=amount_of_entries
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'csv_data_source_failure, expected_reason',
        [
            (CsvDataSourceDependenciesFailure(reason=''), ''),
            (CsvDataSourceDependenciesFailure(reason='T7KHF'), 'T7KHF'),
        ]
    )
    async def test_fetch_should_return_dependencies_failure(
        self,
        csv_data_source_failure: CsvDataSourceFailure,
        expected_reason: str
    ) -> None:
        self._decoy.when(
            await self._dummy_csv_data_source.load()
        ).then_return(Result.error(csv_data_source_failure))

        result: Result[list[PriceEntry], PriceRepositoryFailure] = await self._repository.fetch()

        assert result.is_err()
        err_result: Error[list[PriceEntry], PriceRepositoryFailure] = typing.cast(Error, result)
        failure: PriceRepositoryFailure = err_result.value

        assert failure == PriceRepositoryDependenciesFailure(reason=expected_reason)

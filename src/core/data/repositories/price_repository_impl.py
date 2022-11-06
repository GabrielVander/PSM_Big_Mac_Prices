import typing

from src.core.data.data_sources.csv_data_source import CsvDataSource, CsvDataSourceFailure, CsvDataSourceFileFailure
from src.core.data.data_sources.models.csv_price_model import CsvPriceModel
from src.core.data.repositories.mappers.csv_price_mapper import CsvPriceMapper, CsvPriceMapperFailure
from src.core.domain.entities.price_entry import PriceEntry
from src.core.domain.repository.price_repository import (
    PriceRepository,
    PriceRepositoryDependenciesFailure, PriceRepositoryFailure,
    PriceRepositoryGenericFailure,
)
from src.core.utils.result import Error, Ok, Result


class PriceRepositoryImpl(PriceRepository):
    _csv_data_source: CsvDataSource
    _csv_price_model_mapper: CsvPriceMapper

    def __init__(self, csv_data_source: CsvDataSource, csv_price_model_mapper: CsvPriceMapper) -> None:
        self._csv_data_source = csv_data_source
        self._csv_price_model_mapper = csv_price_model_mapper

    async def fetch(self) -> Result[list[PriceEntry], PriceRepositoryFailure]:
        csv_models_result: Result[list[CsvPriceModel], CsvDataSourceFailure] = await self._load_models()

        if csv_models_result.is_err():
            err_result: Error[list[CsvPriceModel], CsvDataSourceFailure] = typing.cast(Error, csv_models_result)
            failure: CsvDataSourceFailure = err_result.value

            return self._handle_failure(failure)

        csv_models_ok_result: Ok = typing.cast(Ok, csv_models_result)
        models: list[CsvPriceModel] = csv_models_ok_result.value

        entities: list[PriceEntry] = self._to_entities(models)

        return Result.ok(entities)

    async def _load_models(self) -> Result[list[CsvPriceModel], CsvDataSourceFailure]:
        csv_models_result: Result[list[CsvPriceModel], CsvDataSourceFailure] = await self._csv_data_source.load()

        return csv_models_result

    def _to_entities(self, models: list[CsvPriceModel]) -> list[PriceEntry]:
        entity_results: list[Result[PriceEntry, CsvPriceMapperFailure]] = [self._csv_price_model_mapper.map(m)
                                                                           for m in models]
        filtered_entities: list[PriceEntry] = [(typing.cast(Ok, e)).value for e in entity_results if e.is_ok()]

        return filtered_entities

    @staticmethod
    def _handle_failure(failure: CsvDataSourceFailure) -> Error[list[PriceEntry], PriceRepositoryFailure]:
        repo_failure: PriceRepositoryFailure = PriceRepositoryGenericFailure()

        if isinstance(failure, CsvDataSourceFileFailure):
            failure = typing.cast(CsvDataSourceFileFailure, failure)
            repo_failure = PriceRepositoryDependenciesFailure(reason=failure.reason)

        return Result.error(repo_failure)

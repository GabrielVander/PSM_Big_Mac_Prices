from __future__ import annotations

import dataclasses
import typing
from collections.abc import Generator

from src.core.domain.entities.price_entry import PriceEntry
from src.core.domain.use_cases.load_prices_use_case import (
    LoadPricesUseCase,
    LoadPricesUseCaseFailure,
    LoadPricesUseCaseGenericFailure,
)
from src.core.utils.result import Error, Ok, Result
from src.features.statistics.domain.entities.average_price_entry import AveragePriceEntry
from src.features.statistics.domain.use_cases.calculate_average_price_per_country_use_case import (
    CalculateAveragePricePerCountryUseCase, CalculateAveragePriceUseCaseFailure,
)
from src.features.statistics.presentation.average_price_per_country_view_model import (
    AveragePricePerCountryViewModel,
    AveragePriceViewModel,
)


class StatisticsController:
    _average_price_use_case: CalculateAveragePricePerCountryUseCase
    _load_prices_use_case: LoadPricesUseCase

    def __init__(
        self,
        load_prices_use_case: LoadPricesUseCase,
        average_price_use_case: CalculateAveragePricePerCountryUseCase,
    ) -> None:
        self._load_prices_use_case = load_prices_use_case
        self._average_price_use_case = average_price_use_case

    async def calculate_average_price(self) -> Result[AveragePricePerCountryViewModel, StatisticsControllerFailure]:
        prices_result: Result[list[PriceEntry], LoadPricesUseCaseFailure] = await self._load_prices_use_case.execute()

        if prices_result.is_err():
            return self._handle_load_prices_failure(prices_result)

        prices_ok_result: Ok[list[PriceEntry], LoadPricesUseCaseFailure] = typing.cast(Ok, prices_result)
        prices: list[PriceEntry] = prices_ok_result.value

        average_result: Result[list[AveragePriceEntry], CalculateAveragePriceUseCaseFailure] = \
            self._average_price_use_case.execute(prices)

        if average_result.is_err():
            return self._handle_calculate_average_failure(average_result)

        average_ok_result: Ok[list[AveragePriceEntry], CalculateAveragePriceUseCaseFailure] = typing.cast(
            Ok,
            average_result
        )
        average_prices: list[AveragePriceEntry] = average_ok_result.value
        average_price_view_models: list[AveragePriceViewModel] = list(self._as_view_models(average_prices))

        return Result.ok(AveragePricePerCountryViewModel(values=average_price_view_models))

    @staticmethod
    def _handle_load_prices_failure(prices_result):
        prices_err_result: Error[list[PriceEntry], LoadPricesUseCaseFailure] = typing.cast(Error, prices_result)
        failure: LoadPricesUseCaseFailure = prices_err_result.value

        if isinstance(failure, LoadPricesUseCaseGenericFailure):
            return Result.error(
                StatisticsControllerFailure(message='Something went wrong while attempting to load prices...')
            )

        return Result.error(
            StatisticsControllerFailure(message='Some unknown error occurred while attempting to load prices...')
        )

    @staticmethod
    def _handle_calculate_average_failure(
        result: Result[list[AveragePriceEntry], CalculateAveragePriceUseCaseFailure]
    ) -> Result[AveragePricePerCountryViewModel, StatisticsControllerFailure]:
        err_result: Error[list[AveragePriceEntry], CalculateAveragePriceUseCaseFailure] = typing.cast(Error, result)
        failure: CalculateAveragePriceUseCaseFailure = err_result.value

        return Result.error(
            StatisticsControllerFailure(
                message=f'Some unknown error occurred while attempting to calculate average prices: {failure.details}'
            )
        )

    @staticmethod
    def _as_view_models(
        average_prices: list[AveragePriceEntry]
    ) -> Generator[AveragePriceViewModel, None, None]:
        for price in average_prices:
            yield AveragePriceViewModel(
                country_name=price.country.value,
                price=str(price.price.value)
            )


@dataclasses.dataclass(frozen=True, kw_only=True)
class StatisticsControllerFailure:
    message: str
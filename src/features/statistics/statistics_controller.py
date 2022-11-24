from __future__ import annotations

import dataclasses
import typing
from collections.abc import Generator

from src.core.domain.entities.price_entry import PriceEntry
from src.core.domain.entities.single_country_price import SingleCountryPrice
from src.core.domain.use_cases.load_prices_use_case import (
    LoadPricesUseCase,
    LoadPricesUseCaseFailure,
    LoadPricesUseCaseGenericFailure,
)
from src.core.utils.option import Option, Some
from src.core.utils.result import Error, Ok, Result
from src.features.statistics.domain.entities.average_price_entry import AveragePriceEntry
from src.features.statistics.domain.use_cases.calculate_average_price_per_country_use_case import (
    CalculateAveragePricePerCountryUseCase, CalculateAveragePriceUseCaseFailure,
)
from src.features.statistics.domain.use_cases.calculate_cheapest_country_use_case import CalculateCheapestCountryUseCase
from src.features.statistics.domain.use_cases.calculate_most_expensive_country_use_case import \
    CalculateMostExpensiveCountryUseCase
from src.features.statistics.presentation.average_price_per_country_view_model import (
    AveragePricePerCountryViewModel,
)
from src.features.statistics.presentation.most_expensive_country_view_model import MessageViewModel
from src.features.statistics.presentation.single_country_price_view_model import SingleCountryPriceViewModel


class StatisticsController:
    _average_price_use_case: CalculateAveragePricePerCountryUseCase
    _load_prices_use_case: LoadPricesUseCase
    _most_expensive_country_use_case: CalculateMostExpensiveCountryUseCase
    _cheapest_country_use_case: CalculateCheapestCountryUseCase

    def __init__(
        self,
        load_prices_use_case: LoadPricesUseCase,
        average_price_use_case: CalculateAveragePricePerCountryUseCase,
        most_expensive_country_use_case: CalculateMostExpensiveCountryUseCase,
    ) -> None:
        self._load_prices_use_case = load_prices_use_case
        self._average_price_use_case = average_price_use_case
        self._most_expensive_country_use_case = most_expensive_country_use_case
        self._cheapest_country_use_case = CalculateCheapestCountryUseCase()

    async def calculate_average_price(self) -> Result[AveragePricePerCountryViewModel, StatisticsControllerFailure]:
        try:
            prices: list[PriceEntry] = await self._load_prices()
        except _LoadPricesFailure as e:
            return self._handle_load_prices_failure(e.result)

        average_result: Result[list[AveragePriceEntry], CalculateAveragePriceUseCaseFailure] = \
            self._average_price_use_case.execute(prices)

        if average_result.is_err():
            return self._handle_calculate_average_failure(average_result)

        average_ok_result: Ok[list[AveragePriceEntry], CalculateAveragePriceUseCaseFailure] = typing.cast(
            Ok,
            average_result
        )
        average_prices: list[AveragePriceEntry] = average_ok_result.value
        average_price_view_models: list[SingleCountryPriceViewModel] = list(self._as_view_models(average_prices))

        return Result.ok(AveragePricePerCountryViewModel(values=average_price_view_models))

    async def get_most_expensive_country(self) -> Result[MessageViewModel, StatisticsControllerFailure]:
        error_view_model: MessageViewModel = MessageViewModel(message='Unable to determine most expensive country.', )

        try:
            prices: list[PriceEntry] = await self._load_prices()
        except _LoadPricesFailure as e:
            return self._handle_load_prices_failure(e.result)

        average_result: Result[list[AveragePriceEntry], CalculateAveragePriceUseCaseFailure] = \
            self._average_price_use_case.execute(prices)

        if isinstance(average_result, Error):
            return Result.ok(error_view_model)

        average_ok_result: Ok[list[AveragePriceEntry], CalculateAveragePriceUseCaseFailure] = typing.cast(
            Ok,
            average_result
        )
        average_prices: list[AveragePriceEntry] = average_ok_result.value

        most_expensive_country_option: Option[SingleCountryPrice] = \
            self._most_expensive_country_use_case.execute(average_prices)

        if most_expensive_country_option.is_empty():
            return Result.ok(error_view_model)

        most_expensive_country_some: Some[SingleCountryPrice] = typing.cast(Some, most_expensive_country_option)
        most_expensive_country: SingleCountryPrice = most_expensive_country_some.value

        return Result.ok(
            MessageViewModel(
                message=f'The most expensive country is {most_expensive_country.country_name.value} with an average '
                        f'price of USD {most_expensive_country.price.value}'
            )
        )

    async def get_cheapest_country(self) -> MessageViewModel:
        try:
            prices: list[PriceEntry] = await self._load_prices()
        except _LoadPricesFailure as e:
            return MessageViewModel(message=str(self._handle_load_prices_failure(e.result)), )

        average_result: Result[list[AveragePriceEntry], CalculateAveragePriceUseCaseFailure] = \
            self._average_price_use_case.execute(prices)

        if isinstance(average_result, Error):
            return MessageViewModel(
                message='Unable to determine cheapest country.',
            )

        average_ok_result: Ok[list[AveragePriceEntry], CalculateAveragePriceUseCaseFailure] = typing.cast(
            Ok,
            average_result
        )
        average_prices: list[AveragePriceEntry] = average_ok_result.value

        cheapest_option: Option[SingleCountryPrice] = self._cheapest_country_use_case.execute(
            average_prices
        )

        if cheapest_option.is_empty():
            return MessageViewModel(
                message='Unable to determine cheapest country.',
            )

        some_most_expensive: Some[SingleCountryPrice] = typing.cast(Some, cheapest_option)
        cheapest_country: SingleCountryPrice = some_most_expensive.value

        return MessageViewModel(
            message=f'The cheapest country is {cheapest_country.country_name.value} with an average '
                    f'price of USD {cheapest_country.price.value}'
        )

    @staticmethod
    def _handle_load_prices_failure(prices_result: Result[list[PriceEntry], LoadPricesUseCaseFailure]) -> Result:
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
    ) -> Generator[SingleCountryPriceViewModel, None, None]:
        for price in average_prices:
            yield SingleCountryPriceViewModel(
                country_name=price.country.value,
                price=str(price.price.value)
            )

    async def _load_prices(self) -> list[PriceEntry]:
        prices_result: Result[list[PriceEntry], LoadPricesUseCaseFailure] = await self._load_prices_use_case.execute()

        if prices_result.is_err():
            raise _LoadPricesFailure(result=prices_result)

        prices_ok_result: Ok[list[PriceEntry], LoadPricesUseCaseFailure] = typing.cast(Ok, prices_result)
        prices: list[PriceEntry] = prices_ok_result.value

        return prices


@dataclasses.dataclass(frozen=True, kw_only=True)
class _LoadPricesFailure(Exception):
    result: Result[list[PriceEntry], LoadPricesUseCaseFailure]


@dataclasses.dataclass(frozen=True, kw_only=True)
class StatisticsControllerFailure:
    message: str

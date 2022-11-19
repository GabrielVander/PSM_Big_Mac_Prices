import dataclasses
import datetime
import typing
from collections.abc import Generator

import decoy
import pytest

from src.core.domain.entities.price import Amount, ExchangeRate, OriginalCurrency, Price
from src.core.domain.entities.price_entry import CountryName, PriceEntry
from src.core.domain.use_cases.load_prices_use_case import (
    LoadPricesUseCase,
    LoadPricesUseCaseFailure,
    LoadPricesUseCaseGenericFailure,
)
from src.core.utils.result import Error, Ok, Result
from src.features.statistics.domain.entities.average_price_entry import AveragePrice, AveragePriceEntry
from src.features.statistics.domain.use_cases.calculate_average_price_per_country_use_case import (
    CalculateAveragePricePerCountryUseCase, CalculateAveragePriceUseCaseFailure,
)
from src.features.statistics.presentation.average_price_per_country_view_model import (
    AveragePricePerCountryViewModel,
    AveragePriceViewModel,
)
from src.features.statistics.statistics_controller import StatisticsController, StatisticsControllerFailure


@dataclasses.dataclass(frozen=True, kw_only=True)
class _LoadPricesUseCaseUnknownFailure(LoadPricesUseCaseFailure):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class _CalculateAveragePriceUseCaseUnknownFailure(CalculateAveragePriceUseCaseFailure):
    pass


class TestStatisticsController:
    _decoy: decoy.Decoy
    _dummy_average_price_use_case: CalculateAveragePricePerCountryUseCase
    _dummy_load_prices_use_case: LoadPricesUseCase
    _controller: StatisticsController

    @pytest.fixture(autouse=True)
    def set_up_and_tear_down(self) -> Generator[None, None, None]:
        # Set Up
        self._decoy = decoy.Decoy()
        self._dummy_average_price_use_case = self._decoy.mock(cls=CalculateAveragePricePerCountryUseCase)
        self._dummy_load_prices_use_case = self._decoy.mock(cls=LoadPricesUseCase)
        self._controller = StatisticsController(
            load_prices_use_case=self._dummy_load_prices_use_case,
            average_price_use_case=self._dummy_average_price_use_case,
        )

        yield

        # Tear Down
        self._decoy.reset()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'failure, expected_message',
        [
            (LoadPricesUseCaseGenericFailure(), 'Something went wrong while attempting to load prices...'),
            (_LoadPricesUseCaseUnknownFailure(), 'Some unknown error occurred while attempting to load prices...'),
        ]
    )
    async def test_calculate_average_price_should_return_failure_if_load_prices_fails(
        self,
        failure: LoadPricesUseCaseFailure,
        expected_message: str,
    ) -> None:
        self._decoy.when(
            await self._dummy_load_prices_use_case.execute()
        ).then_return(Result.error(failure))

        result: Result[AveragePricePerCountryViewModel, StatisticsControllerFailure] = await \
            self._controller.calculate_average_price()

        assert result.is_err()

        err_result: Error[AveragePricePerCountryViewModel, StatisticsControllerFailure] = typing.cast(Error, result)

        assert err_result.value.message == expected_message

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'entries, failure, expected_message',
        [
            (
                [],
                _CalculateAveragePriceUseCaseUnknownFailure(details=''),
                'Some unknown error occurred while attempting to calculate average prices: '
            ),
            (
                [PriceEntry(
                    country_name=CountryName(value=''),
                    price=Price(
                        amount_in_dollars=Amount(value=0.0),
                        amount_in_original_currency=Amount(value=0.0),
                        original_currency=OriginalCurrency(value=''),
                        dollar_exchange_rate=ExchangeRate(value=0.0)
                    ),
                    date=datetime.date(year=2022, month=11, day=19)
                )],
                _CalculateAveragePriceUseCaseUnknownFailure(details='fFjS'),
                'Some unknown error occurred while attempting to calculate average prices: fFjS'
            ),
        ]
    )
    async def test_calculate_average_price_should_return_failure_if_calculation_fails(
        self,
        entries: list[PriceEntry],
        failure: CalculateAveragePriceUseCaseFailure,
        expected_message: str,
    ) -> None:
        self._decoy.when(
            await self._dummy_load_prices_use_case.execute()
        ).then_return(Result.ok(entries))

        self._decoy.when(
            self._dummy_average_price_use_case.execute(entries)
        ).then_return(Result.error(failure))

        result: Result[AveragePricePerCountryViewModel, StatisticsControllerFailure] = await \
            self._controller.calculate_average_price()

        assert result.is_err()

        err_result: Error[AveragePricePerCountryViewModel, StatisticsControllerFailure] = typing.cast(Error, result)

        assert err_result.value.message == expected_message

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'entries, average_price_entries, expected_view_model',
        [
            ([], [], AveragePricePerCountryViewModel(values=[])),
            (
                [
                    PriceEntry(
                        country_name=CountryName(value=''),
                        price=Price(
                            amount_in_dollars=Amount(value=0.0),
                            amount_in_original_currency=Amount(value=0.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=0.0)
                        ),
                        date=datetime.date(year=2022, month=11, day=19)
                    ),
                ],
                [
                    AveragePriceEntry(
                        country=CountryName(value=''),
                        price=AveragePrice(value=0.0),
                    ),
                ],
                AveragePricePerCountryViewModel(
                    values=[
                        AveragePriceViewModel(
                            country_name='',
                            price='0.0',
                        )
                    ]
                )
            ),
        ]
    )
    async def test_calculate_average_price(
        self,
        entries: list[PriceEntry],
        average_price_entries: list[AveragePriceEntry],
        expected_view_model: AveragePricePerCountryViewModel
    ) -> None:
        assert len(entries) == len(average_price_entries)

        self._decoy.when(
            await self._dummy_load_prices_use_case.execute()
        ).then_return(Result.ok(entries))

        self._decoy.when(
            self._dummy_average_price_use_case.execute(entries)
        ).then_return(Result.ok(average_price_entries))

        result: Result[AveragePricePerCountryViewModel, StatisticsControllerFailure] = await \
            self._controller.calculate_average_price()

        assert result.is_ok()

        ok_result: Ok[AveragePricePerCountryViewModel, StatisticsControllerFailure] = typing.cast(Ok, result)

        assert ok_result.value == expected_view_model

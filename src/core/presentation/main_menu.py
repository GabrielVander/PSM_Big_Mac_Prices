from __future__ import annotations

import abc
import dataclasses
import typing
from collections.abc import Awaitable, Callable, Generator

from src.core.utils.result import Error, Ok, Result
from src.features.price_provisioning.price_provisioning_controller import (
    PriceProvisioningController,
    PriceProvisioningControllerFailure, ProvisionedPricesViewModel,
)
from src.features.statistics.presentation.average_price_per_country_view_model import AveragePricePerCountryViewModel
from src.features.statistics.statistics_controller import StatisticsController, StatisticsControllerFailure


class MainMenu:
    _options: list[_Option]
    _price_provisioning_controller: PriceProvisioningController
    _statistics_controller: StatisticsController

    def __init__(
        self,
        price_provisioning_controller: PriceProvisioningController,
        statistics_controller: StatisticsController,
    ) -> None:
        self._price_provisioning_controller = price_provisioning_controller
        self._statistics_controller = statistics_controller
        self._options = [
            _AsyncOption(id=1, display_message='Display raw data', on_select=self._display_raw_data),
            _SyncOption(
                id=0,
                display_message='Exit (WIP)',
                on_select=lambda: None,
            ),
            _AsyncOption(
                id=2,
                display_message='Calculate average price per country',
                on_select=self._calculate_average_prices,
            ),
            _SyncOption(
                id=3,
                display_message='Get most expensive country on average (WIP)',
                on_select=lambda: None,
            ),
            _SyncOption(
                id=4,
                display_message='Get cheapest country on average (WIP)',
                on_select=lambda: None,
            ),
            _SyncOption(
                id=5,
                display_message='Calculate price change per country (WIP)',
                on_select=lambda: None,
            ),
        ]

    async def run(self) -> None:
        self._display_header()
        self._display_options()
        await self._get_and_run_user_choice()

    def _display_options(self):
        options: list[_Option] = self._options
        options.sort(key=lambda o: o.id)

        for opt in options:
            print(f'{opt.id} - {opt.display_message}')

    async def _get_and_run_user_choice(self):
        available_options: list[int] = list(map(lambda o: o.id, self._options))
        maximum_attempts: int = 20

        for _ in range(maximum_attempts):
            result: str = input('\nChoose an option...\n')

            if result.isnumeric() and (choice_id := int(result)) in available_options:
                await self._select_option_with_id(choice_id)
                return

    async def _select_option_with_id(self, choice_id: int) -> None:
        filtered_options: list[_Option] = list(filter(lambda o: o.id == choice_id, self._options))

        if selected_option := filtered_options[0]:
            if isinstance(selected_option, _AsyncOption):
                async_option: _AsyncOption = typing.cast(_AsyncOption, selected_option)
                await async_option.on_select()

    async def _display_raw_data(self) -> None:
        raw_prices_result: Result[ProvisionedPricesViewModel, PriceProvisioningControllerFailure] = \
            await self._price_provisioning_controller.provision_prices()

        if raw_prices_result.is_ok():
            raw_prices_ok_result: Ok[ProvisionedPricesViewModel, PriceProvisioningControllerFailure] = typing.cast(
                Ok, raw_prices_result
            )

            self._display_prices(raw_prices_ok_result.value)

    async def _calculate_average_prices(self) -> None:
        average_prices_result: Result[AveragePricePerCountryViewModel, StatisticsControllerFailure] = await \
            self._statistics_controller.calculate_average_price()

        if average_prices_result.is_err():
            return self._handle_failure(average_prices_result)

        average_prices_ok_result: Ok[AveragePricePerCountryViewModel, StatisticsControllerFailure] = typing.cast(
            Ok,
            average_prices_result
        )
        average_price_view_model: AveragePricePerCountryViewModel = average_prices_ok_result.value

        self._display_average_prices(average_price_view_model)

    @staticmethod
    def _handle_failure(result: Result[typing.Any, typing.Any]) -> None:
        err_result: Error = typing.cast(Error, result)

        print(str(err_result.value))

    @staticmethod
    def _display_header() -> None:
        _Header(100).display()

    @staticmethod
    def _display_prices(view_model: ProvisionedPricesViewModel) -> None:
        _RawDataDisplayer(view_model=view_model).run()

    @staticmethod
    def _display_average_prices(average_price_view_model: AveragePricePerCountryViewModel) -> None:
        _AveragePriceDisplayer(view_model=average_price_view_model).run()


class _Header:
    _lines: list[str]

    def __init__(self, width: int) -> None:
        self._lines = [
            ' Big Mac Prices '.center(width, '-')
        ]

    def display(self) -> None:
        text: str = '\n'.join(self._lines)

        print(text)


@dataclasses.dataclass(frozen=True, kw_only=True)
class _Option(abc.ABC):
    id: int
    display_message: str


@dataclasses.dataclass(frozen=True, kw_only=True)
class _SyncOption(_Option):
    on_select: Callable[[], None]


@dataclasses.dataclass(frozen=True, kw_only=True)
class _AsyncOption(_Option):
    on_select: Callable[[], Awaitable[None]]


class _RawDataDisplayer:
    _view_model: ProvisionedPricesViewModel

    def __init__(self, view_model: ProvisionedPricesViewModel) -> None:
        self._view_model = view_model

    def run(self) -> None:
        lines: list[str] = list(self._generate_lines())

        print('\n'.join(lines))

    def _generate_lines(self) -> Generator[str, None, None]:
        separator: str = '-' * 15

        for i, price in enumerate(self._view_model.prices):
            yield separator
            yield f'Entry #{i + 1}:'
            yield f'Country Name: {price.country_name}'
            yield f'Price in USD: {price.price_in_dollars}'
            yield f'Local Currency: {price.local_currency_code}'
            yield f'Price in local currency: {price.price_in_local_currency}'
            yield f'USD exchange rate: {price.dollar_exchange_rate}'
            yield f'Date: {price.date}'


class _AveragePriceDisplayer:
    _view_model: AveragePricePerCountryViewModel

    def __init__(self, view_model: AveragePricePerCountryViewModel) -> None:
        self._view_model = view_model

    def run(self) -> None:
        lines: list[str] = list(self._generate_lines())

        print('\n'.join(lines))

    def _generate_lines(self) -> Generator[str, None, None]:
        divisor: str = '-' * 15

        for price in self._view_model.values:
            yield divisor
            yield f'Country: {price.country_name}'
            yield f'Average price in USD: {price.price}'

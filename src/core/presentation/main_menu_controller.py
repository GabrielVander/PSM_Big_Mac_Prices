import datetime
import sys
import typing
from collections.abc import Generator

from src.core.presentation.view_models.main_menu_view_model import MainMenuViewModel
from src.core.utils.option import Option, Some
from src.core.utils.result import Ok, Result
from src.features.price_loading.domain.use_cases.load_prices_use_case import LoadPricesUseCase
from src.features.price_loading.entities.price_entry import CountryName, PriceEntry
from src.features.statistics.domain.entities.average_price_entry import AveragePriceEntry
from src.features.statistics.domain.entities.country_extremes import CountryExtremes
from src.features.statistics.domain.entities.price_change import PriceChange
from src.features.statistics.domain.entities.single_country_price import SingleCountryPrice
from src.features.statistics.domain.use_cases.calculate_average_price_per_country_use_case import (
    CalculateAveragePricePerCountryUseCase, CalculateAveragePriceUseCaseFailure,
)
from src.features.statistics.domain.use_cases.calculate_cheapest_country_use_case import CalculateCheapestCountryUseCase
from src.features.statistics.domain.use_cases.calculate_most_expensive_country_use_case import \
    CalculateMostExpensiveCountryUseCase
from src.features.statistics.domain.use_cases.calculate_price_change_use_case import CalculatePriceChangeUseCase
from src.features.statistics.domain.use_cases.get_extremities_per_country_use_case import \
    GetExtremitiesPerCountryUseCase


class MainMenuController:
    _load_prices_use_case: LoadPricesUseCase
    _average_price_per_country_use_case: CalculateAveragePricePerCountryUseCase
    _most_expensive_country_use_case: CalculateMostExpensiveCountryUseCase
    _cheapest_country_use_case: CalculateCheapestCountryUseCase
    _get_extremities_per_country_use_case: GetExtremitiesPerCountryUseCase
    _calculate_price_change_use_case: CalculatePriceChangeUseCase

    _view_model: MainMenuViewModel
    _prices_cache: list[PriceEntry] | None = None

    def __init__(
        self,
        load_prices_use_case: LoadPricesUseCase,
        calculate_average_price_per_country_use_case: CalculateAveragePricePerCountryUseCase,
        calculate_most_expensive_country_use_case: CalculateMostExpensiveCountryUseCase,
        calculate_cheapest_country_use_case: CalculateCheapestCountryUseCase,
        get_extremities_per_country_use_case: GetExtremitiesPerCountryUseCase,
        calculate_price_change_use_case: CalculatePriceChangeUseCase,
    ) -> None:
        self._load_prices_use_case = load_prices_use_case
        self._average_price_per_country_use_case = calculate_average_price_per_country_use_case
        self._most_expensive_country_use_case = calculate_most_expensive_country_use_case
        self._cheapest_country_use_case = calculate_cheapest_country_use_case
        self._get_extremities_per_country_use_case = get_extremities_per_country_use_case
        self._calculate_price_change_use_case = calculate_price_change_use_case

        self._view_model = MainMenuViewModel(
            title=' Big Mac Prices '.center(150, '-'),
            body=self._options_as_body(),
            option_input_message='Please select an option:\n',
        )

    @property
    def _prices(self) -> list[PriceEntry]:
        self._load_prices()
        return typing.cast(list[PriceEntry], self._prices_cache)

    @property
    def _average_prices_per_country(self) -> list[AveragePriceEntry]:
        average_prices_result: Result[list[AveragePriceEntry], CalculateAveragePriceUseCaseFailure] = \
            self._average_price_per_country_use_case.execute(self._prices)

        if average_prices_result.is_err():
            return []

        average_prices_ok_result: Ok[list[AveragePriceEntry], CalculateAveragePriceUseCaseFailure] \
            = typing.cast(Ok, average_prices_result)

        return average_prices_ok_result.value

    async def display(self) -> MainMenuViewModel:
        await self._load_prices()

        return self._view_model

    async def on_option_selected(self, result: str) -> str:
        selected_option: int = int(result)

        match selected_option:
            case 1:
                if self._prices_cache is not None:
                    return self._display_raw_data(self._prices_cache)
            case 2:
                return self._display_average_price_per_country()
            case 3:
                return self._display_most_expensive_country()
            case 4:
                return self._display_cheapest_country()
            case 5:
                return self._display_price_change_per_country()
            case 0:
                sys.exit()
            case _:
                return 'Invalid option'

        return 'Something weird happened...'

    def _display_price_change_per_country(self) -> str:
        extremities: list[CountryExtremes] = self._get_extremities_per_country_use_case.execute(self._prices)
        price_changes: list[PriceChange] = self._calculate_price_change_use_case.execute(extremities)

        lines: list[str] = list(self._price_changes_as_lines(price_changes))

        return '\n'.join(lines)

    async def _load_prices(self):
        if self._prices_cache is None:
            self._prices_cache = await self._load_prices_use_case.execute()

    def _display_raw_data(self, prices: list[PriceEntry]) -> str:
        if len(prices) == 0:
            return 'No prices found'

        prices_as_raw_lines: list[str] = []

        for p in prices:
            raw_lines: list[str] = list(self._price_as_raw_lines(p))
            prices_as_raw_lines.extend(raw_lines)

        body: str = '\n'.join(prices_as_raw_lines)

        return body

    def _display_average_price_per_country(self) -> str:
        prices_as_raw_lines: list[str] = []

        for p in self._average_prices_per_country:
            raw_lines: list[str] = list(self._average_price_as_raw_lines(p))
            prices_as_raw_lines.extend(raw_lines)

        body: str = '\n'.join(prices_as_raw_lines)

        return body

    def _display_most_expensive_country(self) -> str:
        most_expensive_country_option: Option[SingleCountryPrice] = \
            self._most_expensive_country_use_case.execute(self._average_prices_per_country)

        if most_expensive_country_option.is_empty():
            return 'Unable to calculate most expensive country'

        some_most_expensive_country: Some[SingleCountryPrice] = typing.cast(Some, most_expensive_country_option)

        lines: list[str] = list(self._single_country_price_as_raw_lines(some_most_expensive_country.value))

        return '\n'.join(lines)

    def _display_cheapest_country(self):
        cheapest_country_option: Option[SingleCountryPrice] = \
            self._cheapest_country_use_case.execute(self._average_prices_per_country)

        if cheapest_country_option.is_empty():
            return 'Unable to calculate cheapest country'

        some_cheapest_country: Some[SingleCountryPrice] = typing.cast(Some, cheapest_country_option)
        lines: list[str] = list(self._single_country_price_as_raw_lines(some_cheapest_country.value))

        return '\n'.join(lines)

    def _price_as_raw_lines(self, price: PriceEntry) -> Generator[str, None, None]:
        yield '-' * 150
        yield self._display_country_name(price.country_name)
        yield 'Price in USD: ' + self._float_as_str(price.price.amount_in_dollars.value)
        yield 'Amount in original currency: {0} {1}'.format(
            price.price.original_currency.value,
            self._float_as_str(price.price.amount_in_original_currency.value)
        )
        yield 'USD exchange rate: ' + self._float_as_str(price.price.dollar_exchange_rate.value)
        yield 'Date: ' + self._date_as_str(price.date)

    def _average_price_as_raw_lines(self, price: AveragePriceEntry) -> Generator[str, None, None]:
        yield '-' * 150
        yield self._display_country_name(price.country)
        yield 'Average price in USD: ' + self._float_as_str(price.price.value)

    def _single_country_price_as_raw_lines(self, value: SingleCountryPrice) -> Generator[str, None, None]:
        yield '-' * 150
        yield self._display_country_name(value.country_name)
        yield 'Average price in USD: ' + self._float_as_str(value.price.value)

    def _price_changes_as_lines(self, price_changes: list[PriceChange]) -> Generator[str, None, None]:
        for p in price_changes:
            yield '-' * 150
            yield self._display_country_name(p.country)
            yield 'Price ' + f'{"decreased" if p.percentage.is_negative else "increased"} by ' \
                             f'{p.percentage.value:.2f}% since first measurement'

    @staticmethod
    def validate_input(result: str) -> bool:
        return not result.isdigit() or int(result) < 0 or int(result) > 6

    @staticmethod
    def _options_as_body() -> str:
        return '\n'.join(
            [
                '1 - Display raw data',
                '2 - Calculate average price per country',
                '3 - Get most expensive country on average',
                '4 - Get cheapest country on average',
                '5 - Calculate price change per country',
                '0 - Exit',
            ]
        )

    @staticmethod
    def _float_as_str(value: float) -> str:
        return f'{round(value, 2):.2f}'

    @staticmethod
    def _date_as_str(date: datetime.date) -> str:
        return date.strftime('%Y.%m.%d')

    @staticmethod
    def _display_country_name(name: CountryName) -> str:
        return 'Country: ' + name.value

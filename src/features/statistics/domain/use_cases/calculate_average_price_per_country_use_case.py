from __future__ import annotations

import dataclasses
import typing

from src.core.domain.entities.price import Amount
from src.core.domain.entities.price_entry import CountryName, PriceEntry
from src.core.utils.result import Result
from src.features.statistics.domain.entities.average_price_entry import AveragePrice, AveragePriceEntry
from src.features.statistics.domain.entities.statistics_failure import StatisticsFailure

PriceSumPerCountry: typing.TypeAlias = dict[CountryName, tuple[Amount, int]]


class CalculateAveragePricePerCountryUseCase:

    def execute(
        self,
        entries: list[PriceEntry]
    ) -> Result[list[AveragePriceEntry], CalculateAveragePriceUseCaseFailure]:
        average_prices: list[AveragePriceEntry] = self._get_average_prices(entries)

        return Result[list[AveragePriceEntry], StatisticsFailure].ok(average_prices)  # type: ignore

    def _get_average_prices(self, entries: list[PriceEntry]) -> list[AveragePriceEntry]:
        sum_per_country: PriceSumPerCountry = self._get_price_sum_per_country(entries)
        averages: list[tuple[CountryName, AveragePrice]] = self._calculate_averages(sum_per_country)

        return list(map(lambda i: AveragePriceEntry(country=i[0], price=i[1]), averages))

    @staticmethod
    def _calculate_averages(sum_per_country: PriceSumPerCountry) -> list[tuple[CountryName, AveragePrice]]:
        averages: list[tuple[CountryName, AveragePrice]] = []

        for i in sum_per_country.items():
            country_name, info = i
            price_sum, count = info

            averages.append((country_name, AveragePrice(value=round(price_sum.value / count, 2))))

        return averages

    @staticmethod
    def _get_price_sum_per_country(entries: list[PriceEntry]) -> PriceSumPerCountry:
        price_sum_per_country: PriceSumPerCountry = {}

        for entry in entries:
            current_amount: Amount = entry.price.amount_in_dollars
            new_amount: Amount = current_amount
            new_count: int = 1
            country_name: CountryName = entry.country_name

            if country_name in price_sum_per_country:
                previous_amount, previous_count = price_sum_per_country[country_name]

                new_amount = Amount(value=previous_amount.value + current_amount.value)
                new_count = previous_count + 1

            price_sum_per_country[country_name] = (new_amount, new_count)

        return price_sum_per_country


@dataclasses.dataclass(frozen=True, kw_only=True)
class CalculateAveragePriceUseCaseFailure:
    details: str

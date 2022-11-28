from collections.abc import Generator

import pytest

from src.core.utils.option import Option, Some
from src.features.price_loading.entities.price_entry import CountryName
from src.features.statistics.domain.entities.average_price_entry import AveragePrice, AveragePriceEntry
from src.features.statistics.domain.entities.single_country_price import SingleCountryPrice
from src.features.statistics.domain.use_cases.calculate_most_expensive_country_use_case import \
    CalculateMostExpensiveCountryUseCase


class TestCalculateMostExpensiveCountryUseCase:
    _use_case: CalculateMostExpensiveCountryUseCase

    @pytest.fixture(autouse=True)
    def set_up_and_tear_down(self) -> Generator[None, None, None]:
        # Set Up
        self._use_case = CalculateMostExpensiveCountryUseCase()

        yield

        # Tear Down

    @pytest.mark.parametrize(
        'entries',
        [
            [],
        ]
    )
    def test_should_return_empty(self, entries: list[AveragePriceEntry]) -> None:
        result: Option[SingleCountryPrice] = self._use_case.execute(entries)

        assert result.is_empty()

    @pytest.mark.parametrize(
        'entries, expected',
        [
            (
                [
                    AveragePriceEntry(
                        country=CountryName(value='affair'),
                        price=AveragePrice(value=658.41),
                    ),
                ],
                SingleCountryPrice(country_name=CountryName(value='affair'), price=AveragePrice(value=658.41)),
            ),
            (
                [
                    AveragePriceEntry(
                        country=CountryName(value='affair'),
                        price=AveragePrice(value=100.0),
                    ),
                    AveragePriceEntry(
                        country=CountryName(value='wise'),
                        price=AveragePrice(value=100.0),
                    ),
                ],
                SingleCountryPrice(country_name=CountryName(value='affair'), price=AveragePrice(value=100)),
            ),
            (
                [
                    AveragePriceEntry(
                        country=CountryName(value='soil'),
                        price=AveragePrice(value=100.0),
                    ),
                    AveragePriceEntry(
                        country=CountryName(value='thing'),
                        price=AveragePrice(value=100.0),
                    ),
                ],
                SingleCountryPrice(country_name=CountryName(value='soil'), price=AveragePrice(value=100)),
            ),
            (
                [
                    AveragePriceEntry(
                        country=CountryName(value='affair'),
                        price=AveragePrice(value=10.0),
                    ),
                    AveragePriceEntry(
                        country=CountryName(value='mercy'),
                        price=AveragePrice(value=12.08),
                    ),
                    AveragePriceEntry(
                        country=CountryName(value='nursery'),
                        price=AveragePrice(value=150.0),
                    ),
                    AveragePriceEntry(
                        country=CountryName(value='engine'),
                        price=AveragePrice(value=91.91),
                    ),
                    AveragePriceEntry(
                        country=CountryName(value='shore'),
                        price=AveragePrice(value=140.0),
                    )
                ],
                SingleCountryPrice(country_name=CountryName(value='nursery'), price=AveragePrice(value=150)),
            ),
        ]
    )
    def test_should_return_expected(self, entries: list[AveragePriceEntry], expected: SingleCountryPrice) -> None:
        assert len(entries) > 0

        result: Option[SingleCountryPrice] = self._use_case.execute(entries)

        assert isinstance(result, Some)
        assert result.value == expected

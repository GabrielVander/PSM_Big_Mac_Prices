import datetime
import typing
from collections.abc import Generator

import pytest

from src.core.utils.result import Ok, Result
from src.features.price_loading.entities.price import Amount, ExchangeRate, OriginalCurrency, Price
from src.features.price_loading.entities.price_entry import CountryName, PriceEntry
from src.features.statistics.domain.entities.average_price_entry import AveragePrice, AveragePriceEntry
from src.features.statistics.domain.use_cases.calculate_average_price_per_country_use_case import (
    CalculateAveragePricePerCountryUseCase, CalculateAveragePriceUseCaseFailure,
)


class TestCalculateAveragePricePerCountryUseCase:
    _use_case: CalculateAveragePricePerCountryUseCase

    @pytest.fixture(autouse=True)
    def set_up_and_tear_down(self) -> Generator[None, None, None]:
        # Set Up
        self._use_case = CalculateAveragePricePerCountryUseCase()

        yield

        # Tear Down

    @pytest.mark.parametrize(
        'entries, expected_results',
        [
            ([], []),
            (
                [
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=0.0),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='still'),
                        date=datetime.date(year=2022, month=11, day=3),
                    )
                ],
                [
                    AveragePriceEntry(
                        country=CountryName(value='still'),
                        price=AveragePrice(value=0.0),
                    )
                ]
            ),
            (
                [
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=927.42),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='citizen'),
                        date=datetime.date(year=2022, month=11, day=3),
                    )
                ],
                [
                    AveragePriceEntry(
                        country=CountryName(value='citizen'),
                        price=AveragePrice(value=927.42),
                    )
                ]
            ),
            (
                [
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=398.55),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='affair'),
                        date=datetime.date(year=2022, month=11, day=3),
                    )
                ],
                [
                    AveragePriceEntry(
                        country=CountryName(value='affair'),
                        price=AveragePrice(value=398.55),
                    )
                ]
            ),
            (
                [
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=0.0),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='affair'),
                        date=datetime.date(year=2022, month=11, day=3),
                    ),
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=0.0),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='citizen'),
                        date=datetime.date(year=2022, month=11, day=3),
                    )

                ],
                [
                    AveragePriceEntry(
                        country=CountryName(value='affair'),
                        price=AveragePrice(value=0.0),
                    ),
                    AveragePriceEntry(
                        country=CountryName(value='citizen'),
                        price=AveragePrice(value=0.0),
                    )
                ]
            ),
            (
                [
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=0.0),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='affair'),
                        date=datetime.date(year=2022, month=11, day=3),
                    ),
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=0.0),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='citizen'),
                        date=datetime.date(year=2022, month=11, day=3),
                    ),
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=0.0),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='confess'),
                        date=datetime.date(year=2022, month=11, day=3),
                    )
                ],
                [
                    AveragePriceEntry(
                        country=CountryName(value='affair'),
                        price=AveragePrice(value=0.0),
                    ),
                    AveragePriceEntry(
                        country=CountryName(value='citizen'),
                        price=AveragePrice(value=0.0),
                    ),
                    AveragePriceEntry(
                        country=CountryName(value='confess'),
                        price=AveragePrice(value=0.0),
                    )
                ]
            ),
            (
                [
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=658.41),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='affair'),
                        date=datetime.date(year=2022, month=11, day=3),
                    ),
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=711.74),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='citizen'),
                        date=datetime.date(year=2022, month=11, day=3),
                    ),
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=611.20),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='confess'),
                        date=datetime.date(year=2022, month=11, day=3),
                    )
                ],
                [
                    AveragePriceEntry(
                        country=CountryName(value='affair'),
                        price=AveragePrice(value=658.41),
                    ),
                    AveragePriceEntry(
                        country=CountryName(value='citizen'),
                        price=AveragePrice(value=711.74),
                    ),
                    AveragePriceEntry(
                        country=CountryName(value='confess'),
                        price=AveragePrice(value=611.20),
                    )
                ]
            ),
            (
                [
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=658.41),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='affair'),
                        date=datetime.date(year=2022, month=11, day=3),
                    ),
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=711.74),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='affair'),
                        date=datetime.date(year=2022, month=11, day=3),
                    ),
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=611.20),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='affair'),
                        date=datetime.date(year=2022, month=11, day=3),
                    )
                ],
                [
                    AveragePriceEntry(
                        country=CountryName(value='affair'),
                        price=AveragePrice(value=660.45),
                    ),
                ]
            ),
            (
                [
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=275.70),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='affair'),
                        date=datetime.date(year=2022, month=11, day=3),
                    ),
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=474.97),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='affair'),
                        date=datetime.date(year=2022, month=11, day=3),
                    ),
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=658.72),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='affair'),
                        date=datetime.date(year=2022, month=11, day=3),
                    )
                ],
                [
                    AveragePriceEntry(
                        country=CountryName(value='affair'),
                        price=AveragePrice(value=469.8),
                    ),
                ]
            ),
            (
                [
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=658.41),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='affair'),
                        date=datetime.date(year=2022, month=11, day=3),
                    ),
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=711.74),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='affair'),
                        date=datetime.date(year=2022, month=11, day=3),
                    ),
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=611.20),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='height'),
                        date=datetime.date(year=2022, month=11, day=3),
                    ),
                    PriceEntry(
                        price=Price(
                            amount_in_dollars=Amount(value=387.28),
                            amount_in_original_currency=Amount(value=1.0),
                            original_currency=OriginalCurrency(value=''),
                            dollar_exchange_rate=ExchangeRate(value=3.0),
                        ),
                        country_name=CountryName(value='height'),
                        date=datetime.date(year=2022, month=11, day=3),
                    )
                ],
                [
                    AveragePriceEntry(
                        country=CountryName(value='affair'),
                        price=AveragePrice(value=685.08),
                    ),
                    AveragePriceEntry(
                        country=CountryName(value='height'),
                        price=AveragePrice(value=499.24),
                    )
                ]

            )
        ]
    )
    def test_should_calculate_correctly(
        self,
        entries: list[PriceEntry],
        expected_results: list[AveragePriceEntry]
    ) -> None:
        result: Result[list[AveragePriceEntry], CalculateAveragePriceUseCaseFailure] = self._use_case.execute(entries)

        assert result.is_ok()

        ok_result: Ok[list[AveragePriceEntry], CalculateAveragePriceUseCaseFailure] = typing.cast(Ok, result)

        assert ok_result.value == expected_results

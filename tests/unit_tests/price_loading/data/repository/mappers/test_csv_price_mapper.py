import datetime
import typing
from collections.abc import Generator

import pytest

from src.core.utils.result import Error, Ok, Result
from src.features.price_loading.data.data_sources.models.csv_price_model import CsvPriceModel
from src.features.price_loading.data.repositories.mappers.csv_price_mapper import (
    CsvPriceMapper,
    CsvPriceMapperFailure,
    CsvPriceMapperGenericFailure,
)
from src.features.price_loading.entities.price import Amount, ExchangeRate, OriginalCurrency, Price
from src.features.price_loading.entities.price_entry import CountryName, PriceEntry


class TestCsvPriceMapper:
    _mapper: CsvPriceMapper

    @pytest.fixture(autouse=True)
    def set_up_and_tear_down(self) -> Generator[None, None, None]:
        # Set Up
        self._mapper = CsvPriceMapper()

        yield

        # Tear Down

    @pytest.mark.parametrize(
        'model, expected_output',
        [
            (
                CsvPriceModel(
                    date='2000-04-01',
                    local_price=2.5,
                    dollar_price=2.5,
                    dollar_ex=1,
                    currency_code='ARS',
                    name='Argentina'
                ),
                PriceEntry(
                    date=datetime.date(year=2000, month=4, day=1),
                    country_name=CountryName(value='Argentina'),
                    price=Price(
                        dollar_exchange_rate=ExchangeRate(value=1),
                        original_currency=OriginalCurrency(value='ARS'),
                        amount_in_original_currency=Amount(value=2.5),
                        amount_in_dollars=Amount(value=2.5)
                    )
                )
            ),
            (
                CsvPriceModel(
                    date='2022-07-01',
                    local_price=69000.0,
                    dollar_price=23417,
                    dollar_ex=23417,
                    currency_code='VND',
                    name='Vietnam'
                ),
                PriceEntry(
                    date=datetime.date(year=2022, month=7, day=1),
                    country_name=CountryName(value='Vietnam'),
                    price=Price(
                        dollar_exchange_rate=ExchangeRate(value=23417),
                        original_currency=OriginalCurrency(value='VND'),
                        amount_in_original_currency=Amount(value=69000.0),
                        amount_in_dollars=Amount(value=23417)
                    )
                )

            ),
        ]
    )
    def test_map(self, model: CsvPriceModel, expected_output: PriceEntry) -> None:
        result: Result[PriceEntry, CsvPriceMapperFailure] = self._mapper.map(model)

        assert result.is_ok()

        ok_result: Ok[PriceEntry, CsvPriceMapperFailure] = typing.cast(
            Ok[PriceEntry, CsvPriceMapperFailure],
            result
        )
        entity: PriceEntry = ok_result.value

        assert entity == expected_output

    @pytest.mark.parametrize(
        'model',
        [
            CsvPriceModel(
                date='',
                local_price=2.5,
                dollar_price=2.5,
                dollar_ex=1,
                currency_code='ARS',
                name='Argentina'
            ),
            CsvPriceModel(
                date='MKe9C2',
                local_price=472.72,
                dollar_price=454.05,
                dollar_ex=1934.26,
                currency_code='8W6gC',
                name='fast'
            )
        ]
    )
    def test_should_return_generic_failure(self, model: CsvPriceModel) -> None:
        result: Result[PriceEntry, CsvPriceMapperFailure] = self._mapper.map(model)

        assert result.is_err()

        error_result: Error[PriceEntry, CsvPriceMapperFailure] = typing.cast(
            Error[PriceEntry, CsvPriceMapperFailure],
            result
        )
        failure: CsvPriceMapperFailure = error_result.value

        assert failure == CsvPriceMapperGenericFailure()

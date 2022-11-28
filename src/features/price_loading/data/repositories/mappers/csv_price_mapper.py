from __future__ import annotations

import abc
import dataclasses
import datetime

from src.core.utils.result import Result
from src.features.price_loading.data.data_sources.models.csv_price_model import CsvPriceModel
from src.features.price_loading.entities.price import Amount, ExchangeRate, OriginalCurrency, Price
from src.features.price_loading.entities.price_entry import CountryName, PriceEntry


class CsvPriceMapper:

    def map(self, model: CsvPriceModel) -> Result[PriceEntry, CsvPriceMapperFailure]:
        try:
            entity: PriceEntry = self._to_entity(model)
        except ValueError:
            return Result.error(CsvPriceMapperGenericFailure())

        return Result.ok(entity)

    def _to_entity(self, model):
        return PriceEntry(
            country_name=CountryName(value=model.name.strip()),
            price=Price(
                original_currency=OriginalCurrency(value=model.currency_code.strip()),
                amount_in_original_currency=Amount(value=model.local_price),
                amount_in_dollars=Amount(value=model.dollar_price),
                dollar_exchange_rate=ExchangeRate(value=model.dollar_ex)
            ),
            date=self._to_date(model.date)
        )

    @staticmethod
    def _to_date(date: str) -> datetime.date:
        return datetime.datetime.strptime(date, '%Y-%m-%d').date()


@dataclasses.dataclass(frozen=True, kw_only=True)
class CsvPriceMapperFailure(abc.ABC):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class CsvPriceMapperGenericFailure(CsvPriceMapperFailure):
    pass

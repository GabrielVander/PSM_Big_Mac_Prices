from __future__ import annotations

import abc
import dataclasses
import datetime

from src.core.data.data_sources.models.csv_price_model import CsvPriceModel
from src.core.domain.entities.price import Amount, ExchangeRate, OriginalCurrency, Price
from src.core.domain.entities.price_entry import CountryName, PriceEntry
from src.core.utils.result import Result


class CsvPriceMapper:

    def map(self, model: CsvPriceModel) -> Result[PriceEntry, CsvPriceMapperFailure]:
        try:
            entity: PriceEntry = self._to_entity(model)
        except ValueError:
            return Result.error(CsvPriceMapperGenericFailure())

        return Result.ok(entity)

    def _to_entity(self, model):
        return PriceEntry(
            country_name=CountryName(value=model.name),
            price=Price(
                original_currency=OriginalCurrency(value=model.currency_code),
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

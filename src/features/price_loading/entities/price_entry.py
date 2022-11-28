from __future__ import annotations

import dataclasses
import datetime

from src.features.price_loading.entities.price import Price


@dataclasses.dataclass(frozen=True, kw_only=True)
class PriceEntry:
    country_name: CountryName
    price: Price
    date: datetime.date


@dataclasses.dataclass(frozen=True, kw_only=True)
class CountryName:
    value: str

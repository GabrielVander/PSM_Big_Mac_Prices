from __future__ import annotations

import dataclasses

from src.features.price_loading.entities.price_entry import CountryName


@dataclasses.dataclass(frozen=True, kw_only=True)
class AveragePriceEntry:
    country: CountryName
    price: AveragePrice


@dataclasses.dataclass(frozen=True, kw_only=True)
class AveragePrice:
    value: float

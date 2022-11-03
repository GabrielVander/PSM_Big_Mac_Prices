from __future__ import annotations

import dataclasses

from src.core.domain.entities.price_entry import CountryName


@dataclasses.dataclass(frozen=True, kw_only=True)
class AveragePricePerCountryViewModel:
    values: list[AveragePriceEntry]


@dataclasses.dataclass(frozen=True, kw_only=True)
class AveragePriceEntry:
    country: CountryName
    price: AveragePrice


@dataclasses.dataclass(frozen=True, kw_only=True)
class AveragePrice:
    value: float

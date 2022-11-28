from __future__ import annotations

import dataclasses

from src.features.price_loading.entities.price_entry import CountryName


@dataclasses.dataclass(frozen=True, kw_only=True)
class PriceChange:
    country: CountryName
    percentage: PriceChangePercentage


@dataclasses.dataclass(frozen=True, kw_only=True)
class PriceChangePercentage:
    is_negative: bool
    value: float

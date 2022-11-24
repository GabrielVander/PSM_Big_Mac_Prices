from __future__ import annotations

import dataclasses

from src.core.domain.entities.price_entry import CountryName


@dataclasses.dataclass(frozen=True, kw_only=True)
class PriceChange:
    country: CountryName
    percentage: PriceChangePercentage


@dataclasses.dataclass(frozen=True, kw_only=True)
class PriceChangePercentage:
    is_negative: bool
    value: float

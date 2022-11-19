from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True, kw_only=True)
class AveragePricePerCountryViewModel:
    values: list[AveragePriceViewModel]


@dataclasses.dataclass(frozen=True, kw_only=True)
class AveragePriceViewModel:
    country_name: str
    price: str

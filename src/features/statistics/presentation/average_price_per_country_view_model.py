from __future__ import annotations

import dataclasses

from src.features.statistics.domain.entities.average_price_entry import AveragePriceEntry


@dataclasses.dataclass(frozen=True, kw_only=True)
class AveragePricePerCountryViewModel:
    values: list[AveragePriceEntry]

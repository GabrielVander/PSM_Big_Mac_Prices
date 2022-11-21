from __future__ import annotations

import dataclasses

from src.features.statistics.presentation.single_country_price_view_model import SingleCountryPriceViewModel


@dataclasses.dataclass(frozen=True, kw_only=True)
class AveragePricePerCountryViewModel:
    values: list[SingleCountryPriceViewModel]

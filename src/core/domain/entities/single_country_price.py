import dataclasses

from src.core.domain.entities.price_entry import CountryName
from src.features.statistics.domain.entities.average_price_entry import AveragePrice


@dataclasses.dataclass(frozen=True, kw_only=True)
class SingleCountryPrice:
    country_name: CountryName
    price: AveragePrice

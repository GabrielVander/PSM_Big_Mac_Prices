import dataclasses

from src.features.price_loading.entities.price import Amount
from src.features.price_loading.entities.price_entry import CountryName


@dataclasses.dataclass(frozen=True, kw_only=True)
class CountryExtremes:
    country: CountryName
    oldest_price: Amount
    newest_price: Amount

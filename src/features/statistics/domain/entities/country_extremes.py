import dataclasses

from src.core.domain.entities.price import Amount
from src.core.domain.entities.price_entry import CountryName


@dataclasses.dataclass(frozen=True, kw_only=True)
class CountryExtremes:
    country: CountryName
    oldest_price: Amount
    newest_price: Amount

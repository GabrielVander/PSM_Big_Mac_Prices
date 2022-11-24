import dataclasses


@dataclasses.dataclass(frozen=True, kw_only=True)
class PriceChangeViewModel:
    country_name: str
    percentage_change: str

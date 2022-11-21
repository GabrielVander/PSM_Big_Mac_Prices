import dataclasses


@dataclasses.dataclass(frozen=True, kw_only=True)
class SingleCountryPriceViewModel:
    country_name: str
    price: str

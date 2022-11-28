import dataclasses


@dataclasses.dataclass(frozen=True, kw_only=True)
class CsvPriceModel:
    date: str
    currency_code: str
    name: str
    local_price: float
    dollar_ex: float
    dollar_price: float

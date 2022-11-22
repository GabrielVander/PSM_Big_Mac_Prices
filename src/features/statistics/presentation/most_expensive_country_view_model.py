import dataclasses


@dataclasses.dataclass(frozen=True, kw_only=True)
class MostExpensiveCountryViewModel:
    message: str

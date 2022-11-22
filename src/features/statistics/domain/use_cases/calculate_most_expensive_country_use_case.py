from src.core.domain.entities.price_entry import PriceEntry
from src.core.domain.entities.single_country_price import SingleCountryPrice
from src.core.utils.option import Option


class CalculateMostExpensiveCountryUseCase:

    def execute(self, entries: list[PriceEntry]) -> Option[SingleCountryPrice]:
        raise NotImplementedError()

from src.core.utils.option import Option
from src.features.statistics.domain.entities.average_price_entry import AveragePriceEntry
from src.features.statistics.domain.entities.single_country_price import SingleCountryPrice


class CalculateCheapestCountryUseCase:

    def execute(self, entries: list[AveragePriceEntry]) -> Option[SingleCountryPrice]:
        if not entries:
            return Option.empty()

        cheapest_country: AveragePriceEntry = self._get_cheapest_entry(entries)

        return Option.some(
            SingleCountryPrice(
                country_name=cheapest_country.country,
                price=cheapest_country.price,
            )
        )

    @staticmethod
    def _get_cheapest_entry(entries: list[AveragePriceEntry]) -> AveragePriceEntry:
        return min(entries, key=lambda entry: entry.price.value)

from src.core.utils.option import Option
from src.features.statistics.domain.entities.average_price_entry import AveragePriceEntry
from src.features.statistics.domain.entities.single_country_price import SingleCountryPrice


class CalculateMostExpensiveCountryUseCase:

    def execute(self, entries: list[AveragePriceEntry]) -> Option[SingleCountryPrice]:
        if not entries:
            return Option.empty()

        most_expensive_country: AveragePriceEntry = self._get_most_expensive_entry(entries)

        return Option.some(
            SingleCountryPrice(
                country_name=most_expensive_country.country,
                price=most_expensive_country.price,
            )
        )

    @staticmethod
    def _get_most_expensive_entry(entries: list[AveragePriceEntry]) -> AveragePriceEntry:
        return max(entries, key=lambda entry: entry.price.value)

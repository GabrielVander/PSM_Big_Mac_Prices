from src.features.statistics.domain.entities.country_extremes import CountryExtremes
from src.features.statistics.domain.entities.price_change import PriceChange, PriceChangePercentage


class CalculatePriceChangeUseCase:

    def execute(self, extremes: list[CountryExtremes]) -> list[PriceChange]:
        return [
            PriceChange(
                country=extreme.country,
                percentage=self._calculate_price_change(extreme),
            )
            for extreme in extremes
        ]

    @staticmethod
    def _calculate_price_change(extreme: CountryExtremes) -> PriceChangePercentage:
        return PriceChangePercentage(
            is_negative=extreme.oldest_price.value > extreme.newest_price.value,
            value=(min(extreme.newest_price.value, extreme.oldest_price.value)
                   / max(extreme.newest_price.value, extreme.oldest_price.value)) * 100,
        )

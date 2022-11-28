from src.features.price_loading.entities.price import Amount
from src.features.price_loading.entities.price_entry import CountryName, PriceEntry
from src.features.statistics.domain.entities.country_extremes import CountryExtremes


class GetExtremitiesPerCountryUseCase:

    def execute(self, prices: list[PriceEntry]) -> list[CountryExtremes]:
        if not prices:
            return []

        grouped_prices: dict[CountryName, list[PriceEntry]] = self._group_prices_by_country(prices)

        return self._as_extremes(grouped_prices)

    def _as_extremes(self, grouped_prices: dict[CountryName, list[PriceEntry]]) -> list[CountryExtremes]:
        return [
            CountryExtremes(
                country=country,
                oldest_price=self._get_oldest_price(prices),
                newest_price=self._get_newest_price(prices),
            )
            for country, prices in grouped_prices.items()
        ]

    @staticmethod
    def _group_prices_by_country(prices: list[PriceEntry]) -> dict[CountryName, list[PriceEntry]]:
        grouped_prices: dict[CountryName, list[PriceEntry]] = {}

        for price in prices:
            if price.country_name not in grouped_prices:
                grouped_prices[price.country_name] = []

            grouped_prices[price.country_name].append(price)

        return grouped_prices

    @staticmethod
    def _get_oldest_price(prices: list[PriceEntry]) -> Amount:
        return min(prices, key=lambda price: price.date).price.amount_in_dollars

    @staticmethod
    def _get_newest_price(prices: list[PriceEntry]) -> Amount:
        return max(prices, key=lambda price: price.date).price.amount_in_dollars

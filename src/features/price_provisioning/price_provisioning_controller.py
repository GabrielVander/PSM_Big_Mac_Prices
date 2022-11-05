from __future__ import annotations

import abc
import dataclasses
import datetime
import typing

from src.core.domain.entities.price_entry import PriceEntry
from src.core.utils.result import Error, Ok, Result
from src.features.price_provisioning.domain.use_cases.load_from_csv_use_case import (
    LoadFromCsvUseCase,
    LoadFromCsvUseCaseFailure,
)


class PriceProvisioningControllerFailure(abc.ABC):
    pass


class PriceProvisioningController:
    _load_from_csv_use_case: LoadFromCsvUseCase

    def __init__(self, load_from_csv_use_case: LoadFromCsvUseCase) -> None:
        self._load_from_csv_use_case = load_from_csv_use_case

    async def provision_prices(self) -> Result[ProvisionedPricesViewModel, PriceProvisioningControllerFailure]:
        prices_result: Result[list[PriceEntry], LoadFromCsvUseCaseFailure] = \
            await self._load_from_csv_use_case.execute()

        if prices_result.is_ok():
            prices_ok_result: Ok[list[PriceEntry], LoadFromCsvUseCaseFailure] = typing.cast(
                Ok[list[PriceEntry], LoadFromCsvUseCaseFailure],
                prices_result
            )

            return Result.ok(self._to_view_model(prices_ok_result.value))

        prices_err_result: Error[list[PriceEntry], LoadFromCsvUseCaseFailure] = typing.cast(
            Error[list[PriceEntry], LoadFromCsvUseCaseFailure],
            prices_result
        )

        failure: LoadFromCsvUseCaseFailure = prices_err_result.value
        return self._handle_failure(failure)

    @staticmethod
    def _to_view_model(prices: list[PriceEntry]) -> ProvisionedPricesViewModel:
        return ProvisionedPricesViewModel(
            prices=[
                PriceViewModel(
                    price_in_dollars=p.price.amount_in_dollars.value,
                    price_in_local_currency=p.price.amount_in_original_currency.value,
                    local_currency_code=p.price.original_currency.value,
                    country_name=p.country_name.value,
                    dollar_exchange_rate=p.price.dollar_exchange_rate.value,
                    date=p.date,
                )
                for p in prices
            ]
        )

    @staticmethod
    def _handle_failure(
        _: LoadFromCsvUseCaseFailure
    ) -> Result[ProvisionedPricesViewModel, PriceProvisioningControllerFailure]:
        return Result.error(PriceProvisioningControllerGenericFailure())


class PriceProvisioningControllerGenericFailure(PriceProvisioningControllerFailure):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class ProvisionedPricesViewModel:
    prices: list[PriceViewModel]


@dataclasses.dataclass(frozen=True, kw_only=True)
class PriceViewModel:
    country_name: str
    local_currency_code: str
    price_in_local_currency: float
    price_in_dollars: float
    dollar_exchange_rate: float
    date: datetime.date

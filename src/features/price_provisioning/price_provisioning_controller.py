import abc
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

    async def provision_prices(self) -> Result[list[PriceEntry], PriceProvisioningControllerFailure]:
        prices_result: Result[list[PriceEntry], LoadFromCsvUseCaseFailure] = \
            await self._load_from_csv_use_case.execute()

        if prices_result.is_ok():
            prices_ok_result: Ok[list[PriceEntry], LoadFromCsvUseCaseFailure] = typing.cast(
                Ok[list[PriceEntry], LoadFromCsvUseCaseFailure],
                prices_result
            )

            return Result.ok(prices_ok_result.value)

        prices_err_result: Error[list[PriceEntry], LoadFromCsvUseCaseFailure] = typing.cast(
            Error[list[PriceEntry], LoadFromCsvUseCaseFailure],
            prices_result
        )

        failure: LoadFromCsvUseCaseFailure = prices_err_result.value
        return self._handle_failure(failure)

    @staticmethod
    def _handle_failure(_: LoadFromCsvUseCaseFailure) -> Result[list[PriceEntry], PriceProvisioningControllerFailure]:
        return Result.error(PriceProvisioningControllerGenericFailure())


class PriceProvisioningControllerGenericFailure(PriceProvisioningControllerFailure):
    pass

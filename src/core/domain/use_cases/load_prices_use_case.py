from __future__ import annotations

import abc
import dataclasses
import typing

from src.core.domain.entities.price_entry import PriceEntry
from src.core.domain.repository.price_repository import PriceRepository, PriceRepositoryFailure
from src.core.utils.result import Ok, Result


class LoadPricesUseCase:
    _price_repository: PriceRepository

    def __init__(self, price_repository: PriceRepository) -> None:
        self._price_repository = price_repository

    async def execute(self) -> Result[list[PriceEntry], LoadPricesUseCaseFailure]:
        prices_result: Result[list[PriceEntry], PriceRepositoryFailure] = await self._price_repository.fetch()

        if prices_result.is_err():
            return self._handle_err_result()

        return self._handle_ok_result(prices_result)

    @staticmethod
    def _handle_err_result():
        return Result.error(LoadPricesUseCaseGenericFailure())

    @staticmethod
    def _handle_ok_result(
        prices_result: Result[list[PriceEntry], PriceRepositoryFailure]
    ) -> Result[list[PriceEntry], LoadPricesUseCaseFailure]:
        prices_ok_result: Ok[list[PriceEntry], PriceRepositoryFailure] = typing.cast(
            Ok[list[PriceEntry], PriceRepositoryFailure],
            prices_result
        )
        prices: list[PriceEntry] = prices_ok_result.value

        return Result.ok(prices)


@dataclasses.dataclass(frozen=True, kw_only=True)
class LoadPricesUseCaseFailure(abc.ABC):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class LoadPricesUseCaseGenericFailure(LoadPricesUseCaseFailure):
    pass

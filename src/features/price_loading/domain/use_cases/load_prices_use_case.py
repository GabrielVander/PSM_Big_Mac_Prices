from __future__ import annotations

import abc
import dataclasses
import typing

from src.core.utils.result import Ok, Result
from src.features.price_loading.entities.price_entry import PriceEntry
from src.features.price_loading.repository.price_repository import PriceRepository, PriceRepositoryFailure


class LoadPricesUseCase:
    _price_repository: PriceRepository

    def __init__(self, price_repository: PriceRepository) -> None:
        self._price_repository = price_repository

    async def execute(self) -> list[PriceEntry]:
        prices_result: Result[list[PriceEntry], PriceRepositoryFailure] = await self._price_repository.fetch()

        if prices_result.is_err():
            return []

        prices_ok_result: Ok[list[PriceEntry], PriceRepositoryFailure] = typing.cast(Ok, prices_result)
        return prices_ok_result.value


@dataclasses.dataclass(frozen=True, kw_only=True)
class LoadPricesUseCaseFailure(abc.ABC):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class LoadPricesUseCaseGenericFailure(LoadPricesUseCaseFailure):
    pass

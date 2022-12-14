from __future__ import annotations

import abc
import dataclasses

from src.core.utils.result import Result
from src.features.price_loading.entities.price_entry import PriceEntry


class PriceRepository(abc.ABC):

    @abc.abstractmethod
    async def fetch(self) -> Result[list[PriceEntry], PriceRepositoryFailure]:
        pass  # pragma: nocover


@dataclasses.dataclass(frozen=True, kw_only=True)
class PriceRepositoryFailure(abc.ABC):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class PriceRepositoryGenericFailure(PriceRepositoryFailure):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class PriceRepositoryDependenciesFailure(PriceRepositoryFailure):
    reason: str

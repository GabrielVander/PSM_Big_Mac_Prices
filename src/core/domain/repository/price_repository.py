from __future__ import annotations

import abc
import dataclasses

from src.core.domain.entities.price_entry import PriceEntry
from src.core.utils.result import Result


class PriceRepository(abc.ABC):

    @abc.abstractmethod
    async def fetch(self) -> Result[list[PriceEntry], PriceRepositoryFailure]:
        pass  # pragma: nocover


@dataclasses.dataclass(frozen=True, kw_only=True)
class PriceRepositoryFailure(abc.ABC):
    pass

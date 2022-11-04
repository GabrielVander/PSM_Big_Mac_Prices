from __future__ import annotations

import abc

from src.core.domain.entities.price_entry import PriceEntry
from src.core.utils.result import Result


class LoadFromCsvUseCase:

    async def execute(self) -> Result[list[PriceEntry], LoadFromCsvUseCaseFailure]:
        pass


class LoadFromCsvUseCaseFailure(abc.ABC):
    pass

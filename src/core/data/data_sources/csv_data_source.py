from __future__ import annotations

import abc
import dataclasses

from src.core.data.data_sources.models.csv_price_model import CsvPriceModel
from src.core.utils.result import Result


class CsvDataSource:

    async def load(self) -> Result[list[CsvPriceModel], CsvDataSourceFailure]:
        pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class CsvDataSourceFailure(abc.ABC):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class CsvDataSourceFileFailure(CsvDataSourceFailure):
    reason: str

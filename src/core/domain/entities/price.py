from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True, kw_only=True)
class Price:
    original_currency: OriginalCurrency
    amount_in_original_currency: Amount
    amount_in_dollars: Amount
    dollar_exchange_rate: ExchangeRate


@dataclasses.dataclass(frozen=True, kw_only=True)
class OriginalCurrency:
    value: str


@dataclasses.dataclass(frozen=True, kw_only=True)
class Amount:
    value: float


@dataclasses.dataclass(frozen=True, kw_only=True)
class ExchangeRate:
    value: float

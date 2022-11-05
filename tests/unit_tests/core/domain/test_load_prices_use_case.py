import typing
from collections.abc import Generator

import decoy
import pytest

from src.core.domain.entities.price_entry import PriceEntry
from src.core.domain.repository.price_repository import PriceRepository, PriceRepositoryFailure
from src.core.domain.use_cases.load_prices_use_case import (
    LoadPricesUseCase,
    LoadPricesUseCaseFailure,
    LoadPricesUseCaseGenericFailure,
)
from src.core.utils.result import Error, Ok, Result


class TestLoadPricesUseCase:
    _decoy: decoy.Decoy
    _dummy_price_repository: PriceRepository
    _use_case: LoadPricesUseCase

    @pytest.fixture(autouse=True)
    def set_up_and_tear_down(self) -> Generator[None, None, None]:
        # Set Up
        self._decoy = decoy.Decoy()
        self._dummy_price_repository = self._decoy.mock(cls=PriceRepository)
        self._use_case = LoadPricesUseCase(
            price_repository=self._dummy_price_repository
        )

        yield

        # Tear Down
        self._decoy.reset()

    @pytest.mark.asyncio
    async def test_should_return_generic_failure(self) -> None:
        dummy_failure: PriceRepositoryFailure = self._decoy.mock(cls=PriceRepositoryFailure)

        self._decoy.when(
            await self._dummy_price_repository.fetch()
        ).then_return(Result.error(dummy_failure))

        result: Result[list[PriceEntry], LoadPricesUseCaseFailure] = await self._use_case.execute()

        assert result.is_err()

        error_result: Error[list[PriceEntry], LoadPricesUseCaseFailure] = typing.cast(
            Error[list[PriceEntry], LoadPricesUseCaseFailure],
            result
        )

        assert error_result.value == LoadPricesUseCaseGenericFailure()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'amount_of_entries',
        [
            0,
            3,
        ]
    )
    async def test_should_return_entries_returned_by_repository(self, amount_of_entries: int) -> None:
        entries: list[PriceEntry] = [self._decoy.mock(cls=PriceEntry) for _ in range(amount_of_entries)]

        self._decoy.when(
            await self._dummy_price_repository.fetch()
        ).then_return(Result.ok(entries))

        result: Result[list[PriceEntry], LoadPricesUseCaseFailure] = await self._use_case.execute()

        assert result.is_ok()

        ok_result: Ok[list[PriceEntry], LoadPricesUseCaseFailure] = typing.cast(
            Ok[list[PriceEntry], LoadPricesUseCaseFailure],
            result
        )

        assert ok_result.value == entries

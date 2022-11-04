import datetime
import typing
from collections.abc import Generator

import decoy
import pytest

from src.core.domain.entities.price import Amount, ExchangeRate, OriginalCurrency, Price
from src.core.domain.entities.price_entry import CountryName, PriceEntry
from src.core.utils.result import Ok, Result
from src.features.price_provisioning.domain.use_cases.load_from_csv_use_case import (
    LoadFromCsvUseCase,
    LoadFromCsvUseCaseFailure,
)
from src.features.price_provisioning.price_provisioning_controller import (
    PriceProvisioningController,
    PriceProvisioningControllerFailure,
)


class TestPriceProvisioningController:
    _decoy: decoy.Decoy
    _dummy_load_from_csv_use_case: LoadFromCsvUseCase
    _controller: PriceProvisioningController

    @pytest.fixture(autouse=True)
    def set_up_and_tear_down(self) -> Generator[None, None, None]:
        # Set Up
        self._decoy = decoy.Decoy()
        self._dummy_load_from_csv_use_case = self._decoy.mock(cls=LoadFromCsvUseCase)
        self._controller = PriceProvisioningController(
            load_from_csv_use_case=self._dummy_load_from_csv_use_case
        )

        yield

        # Tear Down
        self._decoy.reset()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'entries',
        [
            [],
            [PriceEntry(
                price=Price(
                    amount_in_dollars=Amount(value=344.93),
                    amount_in_original_currency=Amount(value=224.07),
                    original_currency=OriginalCurrency(value='pencil'),
                    dollar_exchange_rate=ExchangeRate(value=554.94),
                ),
                country_name=CountryName(value='critic'),
                date=datetime.date(year=2022, month=11, day=3),
            )],
            [
                PriceEntry(
                    price=Price(
                        amount_in_dollars=Amount(value=344.93),
                        amount_in_original_currency=Amount(value=224.07),
                        original_currency=OriginalCurrency(value='pencil'),
                        dollar_exchange_rate=ExchangeRate(value=554.94),
                    ),
                    country_name=CountryName(value='critic'),
                    date=datetime.date(year=2022, month=11, day=3),
                ),
                PriceEntry(
                    price=Price(
                        amount_in_dollars=Amount(value=457.05),
                        amount_in_original_currency=Amount(value=340.49),
                        original_currency=OriginalCurrency(value='consider'),
                        dollar_exchange_rate=ExchangeRate(value=618.24),
                    ),
                    country_name=CountryName(value='fact'),
                    date=datetime.date(year=2022, month=11, day=4),
                )
            ]
        ]
    )
    async def test_provision_prices_should_return_ok_result(self, entries: list[PriceEntry]) -> None:
        self._decoy.when(
            await self._dummy_load_from_csv_use_case.execute()
        ).then_return(Result[list[PriceEntry], LoadFromCsvUseCaseFailure].ok(entries))  # type: ignore

        result: Result[list[PriceEntry], PriceProvisioningControllerFailure] = await self._controller.provision_prices()

        assert result.is_ok()

        ok_result: Ok[list[PriceEntry], PriceProvisioningControllerFailure] = typing.cast(
            Ok[list[PriceEntry], PriceProvisioningControllerFailure],
            result
        )

        assert ok_result.value == entries

    @pytest.mark.asyncio
    async def test_provision_prices_should_return_generic_failure(self) -> None:
        load_failure: LoadFromCsvUseCaseFailure = self._decoy.mock(cls=LoadFromCsvUseCaseFailure)

        self._decoy.when(
            await self._dummy_load_from_csv_use_case.execute()
        ).then_return(Result.error(load_failure))

        result: Result[list[PriceEntry], PriceProvisioningControllerFailure] = await self._controller.provision_prices()

        assert result.is_err()

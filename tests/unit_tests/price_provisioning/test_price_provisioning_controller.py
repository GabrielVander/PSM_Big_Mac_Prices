import datetime
import typing
from collections.abc import Generator

import decoy
import pytest

from src.core.domain.entities.price import Amount, ExchangeRate, OriginalCurrency, Price
from src.core.domain.entities.price_entry import CountryName, PriceEntry
from src.core.domain.use_cases.load_prices_use_case import LoadPricesUseCase, LoadPricesUseCaseFailure
from src.core.utils.result import Ok, Result
from src.features.price_provisioning.price_provisioning_controller import (
    PriceProvisioningController,
    PriceProvisioningControllerFailure, PriceViewModel, ProvisionedPricesViewModel,
)


class TestPriceProvisioningController:
    _decoy: decoy.Decoy
    _dummy_load_prices_use_case: LoadPricesUseCase
    _controller: PriceProvisioningController

    @pytest.fixture(autouse=True)
    def set_up_and_tear_down(self) -> Generator[None, None, None]:
        # Set Up
        self._decoy = decoy.Decoy()
        self._dummy_load_prices_use_case = self._decoy.mock(cls=LoadPricesUseCase)
        self._controller = PriceProvisioningController(
            load_prices_use_case=self._dummy_load_prices_use_case
        )

        yield

        # Tear Down
        self._decoy.reset()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'entries, expected',
        [
            ([], ProvisionedPricesViewModel(prices=[])),
            (
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
                    )
                ],
                ProvisionedPricesViewModel(
                    prices=[
                        PriceViewModel(
                            country_name='critic',
                            dollar_exchange_rate='554.94',
                            price_in_dollars='344.93',
                            date='2022.11.03',
                            price_in_local_currency='224.07',
                            local_currency_code='pencil',
                        )
                    ]
                )
            ),
            (
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
                ],
                ProvisionedPricesViewModel(
                    prices=[
                        PriceViewModel(
                            country_name='critic',
                            dollar_exchange_rate='554.94',
                            price_in_dollars='344.93',
                            date='2022.11.03',
                            price_in_local_currency='224.07',
                            local_currency_code='pencil',
                        ),
                        PriceViewModel(
                            country_name='fact',
                            dollar_exchange_rate='618.24',
                            price_in_dollars='457.05',
                            date='2022.11.04',
                            price_in_local_currency='340.49',
                            local_currency_code='consider',
                        ),
                    ]
                )
            ),
        ]
    )
    async def test_provision_prices_should_return_ok_result(
        self,
        entries: list[PriceEntry],
        expected: ProvisionedPricesViewModel
    ) -> None:
        self._decoy.when(
            await self._dummy_load_prices_use_case.execute()
        ).then_return(Result[list[PriceEntry], LoadPricesUseCaseFailure].ok(entries))  # type: ignore

        result: Result[ProvisionedPricesViewModel, PriceProvisioningControllerFailure] = \
            await self._controller.provision_prices()

        assert result.is_ok()

        ok_result: Ok[ProvisionedPricesViewModel, PriceProvisioningControllerFailure] = typing.cast(
            Ok[ProvisionedPricesViewModel, PriceProvisioningControllerFailure],
            result
        )

        assert ok_result.value == expected

    @pytest.mark.asyncio
    async def test_provision_prices_should_return_generic_failure(self) -> None:
        load_failure: LoadPricesUseCaseFailure = self._decoy.mock(cls=LoadPricesUseCaseFailure)

        self._decoy.when(
            await self._dummy_load_prices_use_case.execute()
        ).then_return(Result.error(load_failure))

        result: Result[ProvisionedPricesViewModel, PriceProvisioningControllerFailure] = \
            await self._controller.provision_prices()

        assert result.is_err()

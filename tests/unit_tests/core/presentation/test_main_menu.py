import builtins
import io
import sys
from collections.abc import Callable, Generator

import decoy
import pytest
from _pytest.monkeypatch import MonkeyPatch

from src.core.presentation.main_menu import MainMenu
from src.core.utils.result import Result
from src.features.price_provisioning.price_provisioning_controller import (
    PriceProvisioningController,
    PriceViewModel, ProvisionedPricesViewModel,
)


class TestMainMenu:
    _decoy: decoy.Decoy
    _dummy_price_provisioning_controller: PriceProvisioningController
    _menu: MainMenu

    @pytest.fixture(autouse=True)
    def set_up_and_tear_down(self) -> Generator[None, None, None]:
        # Set Up
        self._decoy = decoy.Decoy()
        self._dummy_price_provisioning_controller = self._decoy.mock(cls=PriceProvisioningController)
        self._menu = MainMenu(
            price_provisioning_controller=self._dummy_price_provisioning_controller,
        )

        yield

        # Tear Down
        self._decoy.reset()

    @pytest.mark.asyncio
    async def test_should_display_correct_message(self, monkeypatch: MonkeyPatch) -> None:
        menu_width: int = 100
        expected_lines: list[str] = [
            ' Big Mac Prices '.center(menu_width, '-'),
            '1 - Display raw data\n',
        ]
        expected_text: str = '\n'.join(expected_lines)
        dummy_input: Callable[[str], str] = self._decoy.mock(func=Callable[[str], str])  # type: ignore
        mock_stdout: io.StringIO = io.StringIO()

        self._decoy.when(
            dummy_input('\nChoose an option...\n')
        ).then_return('Some Option')

        monkeypatch.setattr(builtins, 'input', dummy_input)
        monkeypatch.setattr(sys, 'stdout', mock_stdout)

        await self._menu.run()

        assert mock_stdout.getvalue() == expected_text

    # noinspection SpellCheckingInspection
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'prices, expected_lines',
        [
            (ProvisionedPricesViewModel(prices=[]), []),
            (ProvisionedPricesViewModel(
                prices=[
                    PriceViewModel(
                        date='',
                        price_in_dollars='',
                        price_in_local_currency='',
                        country_name='',
                        dollar_exchange_rate='',
                        local_currency_code='',
                    ),
                ]
            ), [
                 '-' * 15,
                 'Entry #1:',
                 'Country Name: ',
                 'Prince in USD: ',
                 'Local Currency: ',
                 'Price in local currency: ',
                 'USD exchange rate: ',
                 'Date: ',
                 '-' * 15,
             ]),
            (ProvisionedPricesViewModel(
                prices=[
                    PriceViewModel(
                        date='S6Tzngi',
                        price_in_dollars='u4H',
                        price_in_local_currency='8M6fM8',
                        country_name='5N2u86',
                        dollar_exchange_rate='2J9w',
                        local_currency_code='u1xc',
                    ),
                ]
            ), [
                 '-' * 15,
                 'Entry #1:',
                 'Country Name: 5N2u86',
                 'Prince in USD: u4H',
                 'Local Currency: u1xc',
                 'Price in local currency: 8M6fM8',
                 'USD exchange rate: 2J9w',
                 'Date: S6Tzngi',
                 '-' * 15,
             ]),
            (ProvisionedPricesViewModel(
                prices=[
                    PriceViewModel(
                        date='S6Tzngi',
                        price_in_dollars='u4H',
                        price_in_local_currency='8M6fM8',
                        country_name='5N2u86',
                        dollar_exchange_rate='2J9w',
                        local_currency_code='u1xc',
                    ),
                    PriceViewModel(
                        date='SKj43n7b',
                        price_in_dollars='K4ZSJ0Q',
                        price_in_local_currency='hL1Wa',
                        country_name='BPr',
                        dollar_exchange_rate='W9Uw5Ul',
                        local_currency_code='0p88',
                    ),
                ]
            ), [
                 '-' * 15,
                 'Entry #1:',
                 'Country Name: 5N2u86',
                 'Prince in USD: u4H',
                 'Local Currency: u1xc',
                 'Price in local currency: 8M6fM8',
                 'USD exchange rate: 2J9w',
                 'Date: S6Tzngi',
                 '-' * 15,
                 '-' * 15,
                 'Entry #2:',
                 'Country Name: BPr',
                 'Prince in USD: K4ZSJ0Q',
                 'Local Currency: 0p88',
                 'Price in local currency: hL1Wa',
                 'USD exchange rate: W9Uw5Ul',
                 'Date: SKj43n7b',
                 '-' * 15,
             ])
        ]
    )
    async def test_raw_data_option_should_trigger_and_display_correctly(
        self,
        prices: ProvisionedPricesViewModel,
        expected_lines: list[str],
        monkeypatch: MonkeyPatch,
    ) -> None:
        expected_text: str = '\n'.join(expected_lines)
        dummy_input: Callable[[str], str] = self._decoy.mock(func=Callable[[str], str])  # type: ignore
        mock_stdout: io.StringIO = io.StringIO()

        self._decoy.when(
            await self._dummy_price_provisioning_controller.provision_prices()
        ).then_return(Result.ok(prices))

        self._decoy.when(
            dummy_input('\nChoose an option...\n')
        ).then_return('1')

        monkeypatch.setattr(builtins, 'input', dummy_input)
        monkeypatch.setattr(sys, 'stdout', mock_stdout)

        await self._menu.run()

        assert expected_text in mock_stdout.getvalue()

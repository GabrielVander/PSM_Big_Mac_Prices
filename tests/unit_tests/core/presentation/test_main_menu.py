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
from src.features.statistics.presentation.average_price_per_country_view_model import (
    AveragePricePerCountryViewModel,
)
from src.features.statistics.presentation.most_expensive_country_view_model import MessageViewModel
from src.features.statistics.presentation.single_country_price_view_model import SingleCountryPriceViewModel
from src.features.statistics.statistics_controller import StatisticsController, StatisticsControllerFailure


class TestMainMenu:
    _decoy: decoy.Decoy
    _dummy_price_provisioning_controller: PriceProvisioningController
    _dummy_statistics_controller: StatisticsController
    _menu: MainMenu

    @pytest.fixture(autouse=True)
    def set_up_and_tear_down(self) -> Generator[None, None, None]:
        # Set Up
        self._decoy = decoy.Decoy()
        self._dummy_price_provisioning_controller = self._decoy.mock(cls=PriceProvisioningController)
        self._dummy_statistics_controller = self._decoy.mock(cls=StatisticsController)
        self._menu = MainMenu(
            price_provisioning_controller=self._dummy_price_provisioning_controller,
            statistics_controller=self._dummy_statistics_controller,
        )

        yield

        # Tear Down
        self._decoy.reset()

    @pytest.mark.asyncio
    async def test_should_display_correct_message(self, monkeypatch: MonkeyPatch) -> None:
        menu_width: int = 100
        expected_lines: list[str] = [
            ' Big Mac Prices '.center(menu_width, '-'),
            '0 - Exit',
            '1 - Display raw data',
            '2 - Calculate average price per country',
            '3 - Get most expensive country on average',
            '4 - Get cheapest country on average',
            '5 - Calculate price change per country (WIP)\n',
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
                 'Price in USD: ',
                 'Local Currency: ',
                 'Price in local currency: ',
                 'USD exchange rate: ',
                 'Date: ',
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
                 'Price in USD: u4H',
                 'Local Currency: u1xc',
                 'Price in local currency: 8M6fM8',
                 'USD exchange rate: 2J9w',
                 'Date: S6Tzngi',
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
                 'Price in USD: u4H',
                 'Local Currency: u1xc',
                 'Price in local currency: 8M6fM8',
                 'USD exchange rate: 2J9w',
                 'Date: S6Tzngi',
                 '-' * 15,
                 'Entry #2:',
                 'Country Name: BPr',
                 'Price in USD: K4ZSJ0Q',
                 'Local Currency: 0p88',
                 'Price in local currency: hL1Wa',
                 'USD exchange rate: W9Uw5Ul',
                 'Date: SKj43n7b',
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

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'view_model, expected_lines',
        [
            (AveragePricePerCountryViewModel(values=[]), []),
            (AveragePricePerCountryViewModel(
                values=[
                    SingleCountryPriceViewModel(
                        country_name='',
                        price='0.0'
                    ),
                ]
            ), [
                 '-' * 15,
                 'Country: ',
                 'Average price in USD: ',
             ]),
        ]
    )
    async def test_average_prices_option_should_trigger_and_display_correctly(
        self,
        view_model: AveragePricePerCountryViewModel,
        expected_lines: list[str],
        monkeypatch: MonkeyPatch,
    ) -> None:
        expected_text: str = '\n'.join(expected_lines)
        dummy_input: Callable[[str], str] = self._decoy.mock(func=Callable[[str], str])  # type: ignore
        mock_stdout: io.StringIO = io.StringIO()

        self._decoy.when(
            await self._dummy_statistics_controller.calculate_average_price()
        ).then_return(Result.ok(view_model))

        self._decoy.when(
            dummy_input('\nChoose an option...\n')
        ).then_return('2')

        monkeypatch.setattr(builtins, 'input', dummy_input)
        monkeypatch.setattr(sys, 'stdout', mock_stdout)

        await self._menu.run()

        assert expected_text in mock_stdout.getvalue()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'failure, expected_lines',
        [
            (StatisticsControllerFailure(message=''), ["StatisticsControllerFailure(message='')"]),
            (StatisticsControllerFailure(message='hBMe'), ["StatisticsControllerFailure(message='hBMe')"]),
        ]
    )
    async def test_average_prices_option_should_display_failure(
        self,
        failure: StatisticsControllerFailure,
        expected_lines: list[str],
        monkeypatch: MonkeyPatch,
    ) -> None:
        expected_text: str = '\n'.join(expected_lines)
        dummy_input: Callable[[str], str] = self._decoy.mock(func=Callable[[str], str])  # type: ignore
        mock_stdout: io.StringIO = io.StringIO()

        self._decoy.when(
            await self._dummy_statistics_controller.calculate_average_price()
        ).then_return(Result.error(failure))

        self._decoy.when(
            dummy_input('\nChoose an option...\n')
        ).then_return('2')

        monkeypatch.setattr(builtins, 'input', dummy_input)
        monkeypatch.setattr(sys, 'stdout', mock_stdout)

        await self._menu.run()

        assert expected_text in mock_stdout.getvalue()

    @pytest.mark.asyncio
    async def test_exit_option_should_call_sys(self, monkeypatch: MonkeyPatch) -> None:
        dummy_sys_exit: Callable[[], None] = self._decoy.mock(func=Callable[[], None])  # type: ignore
        dummy_input: Callable[[str], str] = self._decoy.mock(func=Callable[[str], str])  # type: ignore
        mock_stdout: io.StringIO = io.StringIO()

        self._decoy.when(
            dummy_input('\nChoose an option...\n')
        ).then_return('0')

        monkeypatch.setattr(builtins, 'input', dummy_input)
        monkeypatch.setattr(sys, 'stdout', mock_stdout)
        monkeypatch.setattr(sys, 'exit', dummy_sys_exit)

        await self._menu.run()

        self._decoy.verify(
            dummy_sys_exit()  # type: ignore
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'view_model, expected_lines',
        [
            (MessageViewModel(message=''), ['']),
            (
                MessageViewModel(
                    message='vertitur prodesset tacimates odio patrioque tamquam dicit tantas lectus decore'
                ),
                ['vertitur prodesset tacimates odio patrioque tamquam dicit tantas lectus decore']
            ),
        ]
    )
    async def test_most_expensive_country_should_trigger_and_display_correctly(
        self,
        view_model: MessageViewModel,
        expected_lines: list[str],
        monkeypatch: MonkeyPatch,
    ) -> None:
        expected_text: str = '\n'.join(expected_lines)
        dummy_input: Callable[[str], str] = self._decoy.mock(func=Callable[[str], str])  # type: ignore
        mock_stdout: io.StringIO = io.StringIO()

        self._decoy.when(
            await self._dummy_statistics_controller.get_most_expensive_country()
        ).then_return(Result.ok(view_model))

        self._decoy.when(
            dummy_input('\nChoose an option...\n')
        ).then_return('3')

        monkeypatch.setattr(builtins, 'input', dummy_input)
        monkeypatch.setattr(sys, 'stdout', mock_stdout)

        await self._menu.run()

        assert expected_text in mock_stdout.getvalue()

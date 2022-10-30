import builtins
import io
import sys
from collections.abc import Callable, Generator

import decoy
import pytest
from _pytest.monkeypatch import MonkeyPatch

from src.core.presentation.main_menu import MainMenu


class TestMainMenu:
    _decoy: decoy.Decoy

    @pytest.fixture(autouse=True)
    def set_up_and_tear_down(self) -> Generator[None, None, None]:
        # Set Up
        self._decoy = decoy.Decoy()

        yield

        # Tear Down
        self._decoy.reset()

    @pytest.mark.asyncio
    async def test_should_display_correct_message(self, monkeypatch: MonkeyPatch) -> None:
        menu_width: int = 100
        expected_lines: list[str] = [
            'Big Mac Prices'.center(menu_width, '-'),
            '1 - Average Price Per Country'.ljust(menu_width, ' ') + '\n',
            'Choose an option...\n'
        ]
        expected_text: str = '\n'.join(expected_lines)
        dummy_input: Callable[[str], str] = self._decoy.mock(func=Callable[[str], str])  # type: ignore
        mock_stdout: io.StringIO = io.StringIO()
        menu: MainMenu = MainMenu()

        self._decoy.when(
            dummy_input('\nChoose an option...\n')
        ).then_return('Some Option')

        monkeypatch.setattr(builtins, 'input', dummy_input)
        monkeypatch.setattr(sys, 'stdout', mock_stdout)

        await menu.run()

        assert mock_stdout.getvalue() == expected_text

import builtins
import io
import sys
from collections.abc import Callable, Generator

import decoy
import pytest
from _pytest.monkeypatch import MonkeyPatch

from src.core.presentation.utils.user_input_menu import UserInputMenu


class TestUserInputMenu:
    _decoy: decoy.Decoy

    @pytest.fixture(autouse=True)
    def set_up_and_tear_down(self) -> Generator[None, None, None]:
        # Set Up
        self._decoy = decoy.Decoy()

        yield

        # Tear Down
        self._decoy.reset()

    # noinspection SpellCheckingInspection
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'display_message',
        [
            '',
            'whoever',
            'table one steel',
            'Fabulas malorum dictumst sea constituto eruditi et fermentum perpetua agam dicunt integer mauris his '
            'necessitatibus vituperatoribus moderatius eirmod maximus velit libero definiebas metus persius congue '
            'voluptatibus no invidunt eruditi magna pro invidunt mollis vidisse ei duo graeco dictas ornatus saperet '
            'mentitum interesset tincidunt eum pellentesque magnis',
            'Fabulas malorum dictumst sea constituto eruditi et fermentum perpetua agam dicunt integer mauris his\n '
            'necessitatibus vituperatoribus moderatius eirmod maximus velit libero definiebas metus persius congue\n '
            'voluptatibus no invidunt eruditi magna pro invidunt mollis vidisse ei duo graeco dictas ornatus saperet\n '
            'mentitum interesset tincidunt eum pellentesque magnis'
        ]
    )
    async def test_should_display_correct_message(self, display_message: str, monkeypatch: MonkeyPatch) -> None:
        mock_stdout: io.StringIO = io.StringIO()

        monkeypatch.setattr(builtins, 'input', lambda _: 'YAY!')
        monkeypatch.setattr(sys, 'stdout', mock_stdout)

        menu: UserInputMenu = UserInputMenu(display_message=display_message)
        await menu.display_until_input()

        assert mock_stdout.getvalue() == display_message

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'user_input',
        [
            '',
            'straw',
        ]
    )
    async def test_should_trigger_on_user_input(self, user_input: str, monkeypatch: MonkeyPatch) -> None:
        message: str = 'Display Message'
        dummy_input_message: str = self._decoy.mock(cls=str)
        mock_stdout: io.StringIO = io.StringIO()
        dummy_input: Callable[[str], str] = self._decoy.mock(func=Callable[[str], str])  # type: ignore
        dummy_on_input: Callable[[str], None] = self._decoy.mock(func=Callable[[str], None])  # type: ignore

        self._decoy.when(
            dummy_input(dummy_input_message)
        ).then_return(user_input)

        monkeypatch.setattr(builtins, 'input', dummy_input)
        monkeypatch.setattr(sys, 'stdout', mock_stdout)

        menu: UserInputMenu = UserInputMenu(
            display_message=message,
            input_message=dummy_input_message,
            on_input=dummy_on_input
        )
        await menu.display_until_input()

        self._decoy.verify(
            dummy_on_input(user_input)  # type: ignore
        )

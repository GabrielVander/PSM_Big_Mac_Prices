from collections.abc import Callable, Generator

import decoy
import pytest

from src.core.presentation.utils.options_menu import Option, OptionsMenu


class TestOptionsMenu:
    _decoy: decoy.Decoy

    @pytest.fixture(autouse=True)
    def set_up_and_tear_down(self) -> Generator[None, None, None]:
        # Set Up
        self._decoy = decoy.Decoy()

        yield

        # Tear Down
        self._decoy.reset()

    @pytest.mark.parametrize(
        'display_messages',
        [
            [''],
            ['musician'],
            ['', ''],
            ['gun', 'depend', 'smoke'],
        ]
    )
    def test_should_display_option_correctly(self, display_messages: list[str]) -> None:
        expected_message: list[str] = [f'{str(i + 1)} - {message}' for i, message in enumerate(display_messages)]
        expected_output: str = '\n'.join(expected_message)

        menu: OptionsMenu = OptionsMenu(options=[Option(display_message=msg) for msg in display_messages])

        display_output: str = menu.display()

        assert display_output == expected_output

    @pytest.mark.parametrize(
        'amount_of_options, target',
        [
            (1, 1),
            (2, 1),
            (3, 1),
            (2, 2),
            (3, 2),
            (3, 3),
            (50, 1),
            (50, 25),
            (50, 50),
        ]
    )
    def test_should_call_given_func_when_selecting_an_option(self, amount_of_options: int, target: int) -> None:
        assert amount_of_options > 0
        assert target in range(1, amount_of_options + 1)

        dummy_func: Callable[[], None] = self._decoy.mock(func=Callable[[], None])
        options: list[Option] = [
            Option(
                display_message=f'Option #{i + 1}',
                on_select=dummy_func if (i + 1) == target else lambda: None
            ) for i in range(amount_of_options)
        ]

        menu: OptionsMenu = OptionsMenu(options=options)
        menu.select(target)

        self._decoy.verify(
            dummy_func(),  # type: ignore
            times=1 if amount_of_options != 0 else 0
        )

    @pytest.mark.parametrize(
        'amount_of_options, target',
        [
            (0, 0),
            (0, 1),
            (0, 5),
            (0, 50),
            (1, 0),
            (1, 2),
            (3, 0),
            (3, 4),
            (50, 0),
            (50, 51),
        ]
    )
    def test_should_not_trigger_any_option_when_giving_an_invalid_target(
        self,
        amount_of_options: int,
        target: int
    ) -> None:
        assert target not in range(1, amount_of_options + 1)

        dummy_func: Callable[[], None] = self._decoy.mock(func=Callable[[], None])
        options: list[Option] = [
            Option(display_message=f'Option #{i + 1}', on_select=dummy_func) for i in range(amount_of_options)
        ]

        menu: OptionsMenu = OptionsMenu(options=options)
        menu.select(target)

        self._decoy.verify(
            dummy_func(),  # type: ignore
            times=0
        )

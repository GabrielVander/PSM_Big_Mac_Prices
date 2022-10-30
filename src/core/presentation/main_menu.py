from __future__ import annotations

from src.core.presentation.utils.options_menu import Option, OptionsMenu
from src.core.presentation.utils.user_input_menu import UserInputMenu


class MainMenu:

    @staticmethod
    async def run() -> None:
        _Header(100).display()
        print(
            OptionsMenu(
                options=[
                    Option(display_message='Average Price Per Country')
                ]
            )
            .display()
            .ljust(100, ' ')
        )
        await UserInputMenu(
            display_message='\nChoose an option...\n',
        ).display_until_input()


class _Header:
    _lines: list[str]

    def __init__(self, width: int) -> None:
        self._lines = [
            'Big Mac Prices'.center(width, '-')
        ]

    def display(self) -> None:
        text: str = '\n'.join(self._lines)

        print(text)

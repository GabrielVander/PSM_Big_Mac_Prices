from __future__ import annotations

from src.core.presentation.main_menu_controller import MainMenuController
from src.core.presentation.view_models.main_menu_view_model import MainMenuViewModel


class MainMenu:
    _controller: MainMenuController

    def __init__(self, main_menu_controller: MainMenuController) -> None:
        self._controller: MainMenuController = main_menu_controller

    async def run(self) -> None:
        view_model: MainMenuViewModel = await self._controller.display()

        self._display_header(view_model.title)
        self._display_body(view_model.body)
        await self._await_user_input(view_model.option_input_message)

    async def _await_user_input(self, input_message: str) -> None:
        result: str = '0'
        should_retry: bool = True

        while should_retry:
            result = input(input_message)
            should_retry = self._controller.validate_input(result)

        display_message: str = await self._controller.on_option_selected(result)
        print(display_message)
        print()

    @staticmethod
    def _display_body(body: str) -> None:
        print(body)

    @staticmethod
    def _display_header(title: str) -> None:
        print(title)

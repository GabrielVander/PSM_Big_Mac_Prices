from collections.abc import Callable


class UserInputMenu:
    _display_message: str
    _input_message: str
    _on_input: Callable[[str], None]

    def __init__(
        self,
        display_message: str,
        input_message: str = '',
        on_input: Callable[[str], None] = lambda _: None
    ) -> None:
        self._display_message = display_message
        self._input_message = input_message
        self._on_input = on_input

    async def display_until_input(self) -> None:
        print(self._display_message, end='')

        user_input: str = input(self._input_message)
        self._on_input(user_input)

from __future__ import annotations

import dataclasses
from collections.abc import Callable, Generator


# TODO: Rename to OptionsBuilder
@dataclasses.dataclass(frozen=True, kw_only=True)
class OptionsMenu:
    options: list[Option]

    def display(self) -> str:
        messages: list[str] = list(self._generate_option_display_messages())

        return '\n'.join(messages)

    def _generate_option_display_messages(self) -> Generator[str, None, None]:
        for index, option in enumerate(self.options):
            raw_message: str = option.display_message

            yield f'{str(index + 1)} - {raw_message}'

    def select(self, target: int) -> None:
        target_index: int = target - 1
        is_valid_target: bool = target_index in range(len(self.options))

        if is_valid_target:
            target_option: Option = self.options[target_index]
            target_option.on_select()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Option:
    display_message: str
    on_select: Callable[[], None] = dataclasses.field(default=lambda: None)

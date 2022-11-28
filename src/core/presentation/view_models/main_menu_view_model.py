from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True, kw_only=True)
class MainMenuViewModel:
    title: str
    body: str
    option_input_message: str

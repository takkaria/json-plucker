from typing import List, Union, Tuple, Optional, Sequence
import re
from dataclasses import dataclass


@dataclass
class NameToken:
    name: str


@dataclass
class ArrayToken:
    pass


Token = Union[NameToken, ArrayToken]


@dataclass
class StartState:
    pass


@dataclass
class SeparatorState:
    first: bool


@dataclass
class NameState:
    captured: str = ""


@dataclass
class ArrayStartState:
    pass


@dataclass
class ArrayEndState:
    pass


@dataclass
class FinishedState:
    pass


State = Union[
    StartState,
    SeparatorState,
    NameState,
    ArrayStartState,
    ArrayEndState,
    FinishedState,
]

NAME = re.compile(r"[a-zA-Z_-]")


class TokeniserError(ValueError):
    message: str
    context: Optional[Tuple[str, int]] = None

    def __init__(self, message):
        self.message = message

    def __str__(self):
        if self.context is None:
            return self.message
        else:
            path, idx = self.context
            return f"{self.message} at index {idx}:\n" + f"{path}\n" + f"{' ' * idx}^"


def _process_char(state: State, ch: Union[str, None]) -> Tuple[State, Optional[Token]]:
    if isinstance(state, StartState):
        if ch != ".":
            raise TokeniserError("All paths should start with the dot")
        else:
            return SeparatorState(first=True), None

    elif isinstance(state, SeparatorState):
        if ch is None:
            if state.first:
                return FinishedState(), None
            else:
                raise TokeniserError("Trailing dot at the end of a path")
        elif re.match(NAME, ch):
            return NameState(captured=ch), None
        elif ch == "[":
            return ArrayStartState(), None
        else:
            raise TokeniserError("Expected a valid name or the start of an array")

    elif isinstance(state, NameState):
        if ch is None:
            return FinishedState(), NameToken(state.captured)
        elif re.match(NAME, ch):
            state.captured += ch
            return state, None
        elif ch == "[":
            return ArrayStartState(), NameToken(state.captured)
        elif ch == ".":
            return SeparatorState(first=False), NameToken(state.captured)
        else:
            raise TokeniserError(f"Was expecting something patching {NAME}")

    elif isinstance(state, ArrayStartState):
        if ch != "]":
            raise TokeniserError("Array indicators should be spelled []")
        else:
            return ArrayEndState(), None

    elif isinstance(state, ArrayEndState):
        # We are expecting either EOF or a separator
        if ch is None:
            return FinishedState(), ArrayToken()
        elif ch == ".":
            return SeparatorState(first=False), ArrayToken()
        else:
            raise TokeniserError(
                "Array end should only be followed by EOF or separator"
            )

    raise TokeniserError("Tokeniser got into a bad state")


def tokenise(path: str) -> List[Token]:
    state: State = StartState()
    tokens: List[Token] = []

    split_path = [*path, None]

    for idx, ch in enumerate(split_path):
        try:
            print(state)
            state, token = _process_char(state, ch)
        except TokeniserError as exc:
            exc.context = path, idx
            raise exc
        else:
            if token:
                tokens += [token]

    assert isinstance(state, FinishedState)
    return tokens

from typing import List, Union, Tuple, Optional
import re
from dataclasses import dataclass


@dataclass
class Range:
    """A range specified as indexes from the beginning of some external referent."""

    start: int
    end: int

    def __len__(self):
        """Calculate the length of a range."""
        return self.end - self.start


# Token types
# -----------
#
# We only have to kinds of tokens at the moment that the tokeniser can emit: names and
# arrays.  Each keeps its own location in the string as a Range.


@dataclass
class NameToken:
    """A token that indexes into a JSON object."""

    location: Range
    name: str


@dataclass
class ArrayToken:
    """A token that tells us we are mapping an array."""

    location: Range


Token = Union[NameToken, ArrayToken]

# Tokeniser errors
# ----------------


class TokeniserError(ValueError):
    """A parse error while tokenising."""

    message: str
    context: Optional[Tuple[str, int]] = None

    def __init__(self, message: str):
        """Initialise a parse error with a message."""
        self.message = message

    def __str__(self):
        """Provide a useful string representation of the error."""
        if self.context is None:
            return self.message
        else:
            path, idx = self.context
            return f"{self.message} at index {idx}:\n" + f"{path}\n" + f"{' ' * idx}^"


# State machine states
# --------------------
#
# We have a bunch of these.  A given state can store different information.


@dataclass
class StartState:
    """Initial state.  Nothing has been parsed yet."""

    pass


@dataclass
class SeparatorState:
    """We have just parsed a dot ('.')."""

    first: bool


@dataclass
class NameState:
    """We are parsing a name."""

    captured: str
    started_at: int


@dataclass
class ArrayStartState:
    """We have read an array start ('[') character."""

    started_at: int


@dataclass
class ArrayEndState:
    """We have read an array end (']') character."""

    started_at: int


@dataclass
class FinishedState:
    """Reached EOF without problems."""

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


def _process_char(  # noqa: C901
    state: State,
    ch: Union[str, None],
    idx: int,
) -> Tuple[State, Optional[Token]]:

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
            return NameState(captured=ch, started_at=idx), None
        elif ch == "[":
            return ArrayStartState(started_at=idx), None
        else:
            raise TokeniserError("Expected a valid name or the start of an array")

    elif isinstance(state, NameState):

        def _name_token(state: NameState) -> NameToken:
            return NameToken(Range(state.started_at, idx), name=state.captured)

        if ch is None:
            return FinishedState(), _name_token(state)
        elif re.match(NAME, ch):
            state.captured += ch
            return state, None
        elif ch == "[":
            return ArrayStartState(started_at=idx), _name_token(state)
        elif ch == ".":
            return SeparatorState(first=False), _name_token(state)
        else:
            raise TokeniserError(f"Was expecting something patching {NAME}")

    elif isinstance(state, ArrayStartState):
        if ch != "]":
            raise TokeniserError("Array indicators should be spelled []")
        else:
            return ArrayEndState(started_at=state.started_at), None

    elif isinstance(state, ArrayEndState):

        def _array_token(state: ArrayEndState) -> ArrayToken:
            return ArrayToken(Range(state.started_at, idx))

        # We are expecting either EOF or a separator
        if ch is None:
            return FinishedState(), _array_token(state)
        elif ch == ".":
            return SeparatorState(first=False), _array_token(state)
        else:
            raise TokeniserError(
                "Array end should only be followed by EOF or separator"
            )

    raise TokeniserError("Tokeniser got into a bad state")


def tokenise(path: str) -> List[Token]:
    """Tokenise a path string, returning a list of tokens or raising TokeniserError."""
    state: State = StartState()
    tokens: List[Token] = []

    # It's useful to have an 'EOF' input, so we use None.
    split_path = [*path, None]

    for idx, ch in enumerate(split_path):
        try:
            print(state)
            state, token = _process_char(state, ch, idx)
        except TokeniserError as exc:
            exc.context = path, idx
            raise exc

        if token:
            print(token)
            tokens += [token]

    assert isinstance(state, FinishedState)
    return tokens

from typing import List, Any, Optional
from .tokeniser import tokenise, Token, ArrayToken, NameToken


class ExtractError(ValueError):
    message: str
    token: Token
    path: Optional[str]

    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
        self.path = None

    def __str__(self):
        if self.path:
            return (
                f"{self.message}:\n"
                f"{self.path}\n"
                f"{' ' * self.token.location.start}{'^' * len(self.token.location)}"
            )
        else:
            return self.message


def _get_from_array(data: Any, head: ArrayToken, rest: List[Token]):
    """
    'data' is a list.  Return a new array containing the contents of each of
    data's entries at location 'path'.

    e.g.

        data = [
            {"u": {"type": "remove"}},
            {"u": {"type": "add"}},
        ]
        path = [NameToken("u"), NameToken("type")]

        _get_from_array(data, path) == ["remove", "add"]

    """

    return [_get_from_path(entry, rest) for entry in data]


def _get_from_name(data: Any, head: NameToken, rest: List[Token]):
    if not isinstance(data, dict):
        raise ExtractError(
            head,
            f"Data not in expected format; expected {head.name} to be 'dict' but it was '{data.__class__.__name__}'",
        )

    try:
        data = data[head.name]
    except KeyError:
        raise ExtractError(head, f"Expected field name {head.name} to exist")

    return _get_from_path(data, rest)


def _get_from_path(data: Any, path: List[Token]):
    if path == []:
        return data

    head = path[0]

    if isinstance(head, NameToken):
        return _get_from_name(data, head, path[1:])
    elif isinstance(head, ArrayToken):
        return _get_from_array(data, head, path[1:])


def extract(data: Any, path: str):
    tokens = tokenise(path)
    try:
        return _get_from_path(data, tokens)
    except ExtractError as exc:
        exc.path = path
        raise exc

from typing import List, Any, Tuple, Dict
from .tokeniser import tokenise, Token, ArrayToken, NameToken
from .exceptions import ExtractError


def _get_array_from_path(
    data: List[Any],
    head: ArrayToken,
    rest: List[Token],
):
    """
    Return a new array containing the contents of each of data's entries at location 'path'.

    e.g.

        data = [
            {"u": {"type": "remove"}},
            {"u": {"type": "add"}},
        ]
        path = [NameToken("u"), NameToken("type")]

        _get_array_from_path(data, path) == ["remove", "add"]

    """
    return [_get_from_path(entry, rest) for entry in data]


def _get_name_from_path(
    data: Dict[str, Any],
    head: NameToken,
    rest: List[Token],
):
    try:
        data = data[head.name]
    except KeyError:
        raise ExtractError(head, f"Expected field name {head.name} to exist")

    return _get_from_path(data, rest)


def _get_from_path(data: Any, path: List[Token]) -> Any:
    if path == []:
        return data

    head = path[0]

    if isinstance(head, NameToken):
        if not isinstance(data, dict):
            raise ExtractError(
                head,
                f"Data not in expected format; expected {head.name} to be 'dict'"
                f" but it was '{data.__class__.__name__}'",
            )

        return _get_name_from_path(data, head, path[1:])

    elif isinstance(head, ArrayToken):
        if not isinstance(data, list):
            # TODO: Check this error makes sense
            raise ExtractError(
                head,
                f"Data not in expected format; expected 'list'"
                f" but it was '{data.__class__.__name__}'",
            )

        return _get_array_from_path(data, head, path[1:])


def extract(data: Any, path: str) -> Tuple[Any, List[Token]]:
    """Navigate an input using a string path, returning the leaf value."""
    tokens = tokenise(path)
    try:
        return _get_from_path(data, tokens), tokens
    except ExtractError as exc:
        exc.path = path
        raise exc

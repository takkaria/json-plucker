from typing import List, Union, Callable, TypeVar, Any
from .tokeniser import tokenise, Token, ArrayToken, NameToken

T = TypeVar("T")


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

    return [get_from_path(entry, rest) for entry in data]


def _get_from_name(data: Any, head: NameToken, rest: List[Token]):
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict, got {type(data)}")

    try:
        data = data[head.name]
    except KeyError:
        raise ValueError(f"Expected field name {head.name} to exist")

    return get_from_path(data, rest)


def get_from_path(data: Any, path: Union[str, List[Token]]):
    if isinstance(path, str):
        path = tokenise(path)

    if path == []:
        return data

    head = path[0]

    if isinstance(head, NameToken):
        return _get_from_name(data, head, path[1:])
    elif isinstance(head, ArrayToken):
        return _get_from_array(data, head, path[1:])

    assert None, "This is a total fail"


class Pluck:
    def __init__(self, path: str):
        self.path: str = path
        self.mapper = None
        self.type = None

    def map(self, mapper: Union[Callable, dict]) -> "Pluck":
        self.mapper = mapper
        return self

    def into(self, __into: T, **kwargs) -> "Pluck":
        self.type = __into
        return self

    def pluck(self, data: Any, expected_type: T) -> T:
        source = get_from_path(data, self.path)

        if self.mapper:
            data = self.mapper(data)

        assert type(source) == type(expected_type)

        return expected_type(data)


def extract(__data: Any, __into: T, **kwargs) -> T:
    attrs = {}
    for attr, plucker in kwargs.items():
        type_of_attr = type.__annotations__[attr]
        attrs[attr] = plucker.pluck(__data, type_of_attr)

    return type(**attrs)

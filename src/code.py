from typing import List, Union, Callable, TypeVar, Any
from enum import Enum, auto
from dataclasses import dataclass
from datetime import date
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
    try:
        data = data[head.name]
    except KeyError:
        raise ValueError(f"Expected field name {head.name} to exist")

    return get_from_path(data, rest)


def get_from_path(data: Any, path: List[Token]):
    head = path[0]

    if isinstance(head, NameToken):
        return _get_from_name(data, head, path[1:])
    elif isinstance(head, ArrayToken):
        return _get_from_array(data, head, path[1:])

    assert None, "This is a total fail"


class Pluck:
    def __init__(self, path: str):
        self.path: List[Token] = tokenise(path)
        self.mapper = None
        self.info = None

    def map(self, mapper: Union[Callable, dict]) -> "Pluck":
        self.mapper = mapper
        return self

    def into(self, into) -> "Pluck":
        self.into = into
        return self

    def pluck(self, data: Any, expected_type: T) -> T:
        source = get_from_path(data, self.path)

        if self.mapper:
            data = self.mapper(data)

        assert type(source) == type(expected_type)

        return None


def parse_into(data: Any, *, into: T, **kwargs) -> T:
    attrs = {}
    for attr, plucker in kwargs.items():
        type_of_attr = type.__annotations__[attr]
        attrs[attr] = plucker.pluck(data, type_of_attr)

    return type(**attrs)


class MemberStatus(Enum):
    CURRENT = auto()
    EXPIRED = auto()


TO_STATUS = {"CUR": MemberStatus.CURRENT, "EXP": MemberStatus.EXPIRED}


@dataclass
class Person:
    name: str
    id: int


@dataclass
class StatusChange:
    date: date
    state_from: Enum[MemberStatus]
    state_to: Enum[MemberStatus]
    ids: List[int]
    num: int


def extract(json: dict) -> StatusChange:
    return extract(
        json,
        into=StatusChange,
        date=Pluck(".date"),
        num=Pluck(".number_as_str").map(int),
        state_from=Pluck(".payload.from").map(TO_STATUS),
        state_to=Pluck(".payload.to").map(TO_STATUS),
        ids=Pluck(".payload.who[].id"),
        people=Pluck(".payload.who[]").into(
            Person,
            name=Pluck(".name"),
            id=Pluck(".id"),
        ),
    )

from typing import Union, Callable, Any, TypeVar
from .tokeniser import tokenise, Token, ArrayToken, NameToken

T = TypeVar("T")


class Path:
    def __init__(self, path: str):
        self.path: str = path
        self.mapper = None
        self.type = None

    def map(self, mapper: Union[Callable, dict]) -> "Path":
        self.mapper = mapper
        return self

    def into(self, __into: T, **kwargs) -> "Path":
        self.type = __into
        return self

    def pluck(self, data: Any, expected_type: T) -> T:
        source = extract(data, self.path)

        if self.mapper:
            data = self.mapper(data)

        assert type(source) == type(expected_type)

        return expected_type(data)


def pluck(__data: Any, __into: T, **kwargs) -> T:
    attrs = {}
    for attr, plucker in kwargs.items():
        type_of_attr = type.__annotations__[attr]
        attrs[attr] = plucker.pluck(__data, type_of_attr)

    return type(**attrs)

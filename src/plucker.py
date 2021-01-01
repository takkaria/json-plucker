from typing import Union, Callable, Any, TypeVar, Type, Optional
from .extractor import extract

T = TypeVar("T")


class Path:
    def __init__(self, path: str):
        self.path: str = path
        self.mapper: Optional[Callable] = None
        self.type: Type = None

    def map(self, mapper: Union[Callable, dict]) -> "Path":
        self.mapper = mapper
        return self

    def into(self, __into: Type, **kwargs) -> "Path":
        self.type = __into
        return self

    def pluck(self, data: Any, expected_type: Type[T]) -> T:
        source = extract(data, self.path)

        print(source)
        print(type(source), expected_type)

        # assert type(source) == expected_type

        return source


def pluck(__data: Any, __into: T, **kwargs) -> T:
    attrs = {}
    for attr, plucker in kwargs.items():
        type_of_attr = __into.__annotations__[attr]
        attrs[attr] = plucker.pluck(__data, type_of_attr)

    print(attrs)

    return __into(**attrs)

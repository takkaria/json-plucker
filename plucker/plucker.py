import typing
from dataclasses import is_dataclass
from typing import Union, Callable, Any, TypeVar, Type, Optional, List

from .extractor import extract
from .tokeniser import Token, ArrayToken, NameToken
from .types import JSONStructure, JSONValue, Mapper

T = TypeVar("T")


def reconstruct_path(tokens: List[Token], indexes: List[int]) -> str:
    path = ""
    cur_idx = 0

    for t in tokens:
        if isinstance(t, NameToken):
            path += f".{t.name}"
        if isinstance(t, ArrayToken):
            path += f"[{indexes[cur_idx]}]"
            cur_idx += 1

    return path


class PluckError(TypeError):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


# This doesn't work for List[List[int]], ie doubly nested, types.
# We will need to rewrite this to be recursive to handle these.
def _typecheck(data: Any, expected_type, tokens: List[Token]):
    e_type: Optional[Any]
    e_subtype: Optional[Any]

    if expected_type.__module__ == "typing":
        e_type = typing.get_origin(expected_type)
        e_subtype = typing.get_args(expected_type)[0]
    else:
        e_type = expected_type
        e_subtype = None

    if e_type is None:
        # TODO: Find a better error message
        raise ValueError("expected_type is none")
        pass

    if e_subtype is None:
        if type(data) != e_type:
            path = reconstruct_path(tokens, [])
            raise PluckError(
                f"{path} should be '{e_type.__name__}' but is '{type(data).__name__}'"
                "instead"
            )
    else:
        if e_type != list:
            raise PluckError(f"Unknown e_type type {e_type}")

        for idx, x in enumerate(data):
            actual_type = type(x)
            if actual_type != e_subtype:
                path = reconstruct_path(tokens, [idx])
                raise PluckError(
                    f"{path} should be '{e_subtype.__name__}' but is"
                    f"'{actual_type.__name__}' instead"
                )


class Path:
    def __init__(self, path: str):
        self.path: str = path
        self.mapper: Optional[Mapper] = None
        self.type: Optional[Type[Any]] = None

    def map(self, mapper: Mapper) -> "Path":
        self.mapper = mapper
        return self

    def into(self, __into: Type[Any], **kwargs) -> "Path":
        self.type = __into
        self.type_kwargs = kwargs
        return self

    def _apply_map(self, data: Any, tokens: List[Token]) -> Any:
        if not self.mapper:
            return data

        if isinstance(self.mapper, dict):
            try:
                return self.mapper[data]
            except KeyError:
                path = reconstruct_path(tokens, [])
                raise PluckError(f"Couldn't map {path} (value is {repr(data)})")
        else:
            try:
                return self.mapper(data)
            except Exception as exc:
                path = reconstruct_path(tokens, [])
                raise PluckError(
                    f"Couldn't map {path} (value is {repr(data)})"
                ) from exc

    def _apply_into(self, data: Any) -> List[T]:
        if not self.type:
            return data
        else:
            return [pluck(row, self.type, **self.type_kwargs) for row in data]

    def pluck(self, data: JSONStructure, expected_type: Type[T]) -> T:
        source, tokens = extract(data, self.path)
        source = self._apply_into(source)
        source = self._apply_map(source, tokens)

        print(source)
        print(type(source), expected_type)
        _typecheck(source, expected_type, tokens)

        return source


def pluck(__data: JSONStructure, __into: Type[T], **kwargs) -> T:
    if not is_dataclass(__into):
        raise ValueError("__into must be a dataclass")

    attrs = {}
    for attr, plucker in kwargs.items():
        type_of_attr = __into.__annotations__[attr]
        attrs[attr] = plucker.pluck(__data, type_of_attr)

    print(attrs)

    return __into(**attrs)  # type: ignore[call-arg]
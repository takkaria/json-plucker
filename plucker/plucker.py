import typing
from dataclasses import is_dataclass
from typing import Any, TypeVar, Type, Optional, List, Tuple, Dict

from .extractor import extract
from .tokeniser import Token, ArrayToken, NameToken
from .types import JSONStructure, Mapper, MapperFn
from .exceptions import PluckError

T = TypeVar("T")


def _reconstruct_path(tokens: List[Token], indexes: List[int]) -> str:
    path = ""
    cur_idx = 0

    for t in tokens:
        if isinstance(t, NameToken):
            path += f".{t.name}"
        if isinstance(t, ArrayToken):
            path += f"[{indexes[cur_idx]}]"
            cur_idx += 1

    return path


def _get_type(
    expected_type: Type[Any],
) -> Tuple[Type[Any], Optional[Type[Any]]]:
    e_type: Optional[Type[Any]]
    e_subtype: Optional[Type[Any]]

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

    return e_type, e_subtype


# This doesn't work for List[List[int]], ie doubly nested, types.
# We will need to rewrite this to be recursive to handle these.
def _typecheck(data: Any, expected_type, tokens: List[Token]):
    e_type, e_subtype = _get_type(expected_type)

    if e_subtype is None:
        if type(data) != e_type:
            path = _reconstruct_path(tokens, [])
            desired_type = e_type.__name__
            type_name = type(data).__name__
            raise PluckError(
                f"{path} should be '{desired_type}' but is '{type_name}' instead"
            )

    else:
        if e_type != list:
            raise PluckError(f"Unknown e_type type {e_type}")

        for idx, x in enumerate(data):
            actual_type = type(x)
            if actual_type != e_subtype:
                path = _reconstruct_path(tokens, [idx])
                desired_type = e_subtype.__name__
                type_name = actual_type.__name__
                raise PluckError(
                    f"{path} should be '{desired_type}' but is '{type_name}' instead"
                )


class Path:
    """A path to a value in a JSON representation."""

    def __init__(self, path: str):
        """Specify a path to fill in as the value part of kwargs passed to `pluck`."""
        self.path: str = path
        self.mapper: Optional[Mapper] = None
        self.type: Optional[Type[Any]] = None

    def map(self, mapper: Mapper) -> "Path":
        """Transform the value in the input using `mapper`."""
        self.mapper = mapper
        return self

    def into(self, __into: Type[Any], **kwargs) -> "Path":
        """Parse the value in the input into another dataclass."""
        self.type = __into
        self.type_kwargs = kwargs
        return self

    @staticmethod
    def _apply_map_dict(mapper: Dict[str, Any], data: Any, tokens: List[Token]) -> Any:
        """Map using a dict, producing an error if necessary."""
        try:
            return mapper[data]
        except KeyError:
            path = _reconstruct_path(tokens, [])
            raise PluckError(f"Couldn't map {path} (value is {repr(data)})")

    @staticmethod
    def _apply_map_fn(mapper: MapperFn, data: Any, tokens: List[Token]) -> Any:
        """Map using a function, producing an error if necessary."""
        try:
            return mapper(data)
        except Exception as exc:
            path = _reconstruct_path(tokens, [])
            raise PluckError(f"Couldn't map {path} (value is {repr(data)})") from exc

    def _apply_map(self, data: Any, tokens: List[Token]) -> Any:
        """Apply mapping if provided."""
        if self.mapper is None:
            return data
        elif isinstance(self.mapper, dict):
            return self._apply_map_dict(self.mapper, data, tokens)
        else:
            return self._apply_map_fn(self.mapper, data, tokens)

    def _apply_into(self, data: Any) -> List[T]:
        if not self.type:
            return data
        else:
            return [pluck(row, self.type, **self.type_kwargs) for row in data]

    def _pluck(self, data: JSONStructure, expected_type: Type[T]) -> T:
        source, tokens = extract(data, self.path)
        source = self._apply_into(source)
        source = self._apply_map(source, tokens)

        print(source)
        print(type(source), expected_type)
        _typecheck(source, expected_type, tokens)

        return source


def pluck(__data: JSONStructure, __into: Type[T], **kwargs: Path) -> T:
    """Pluck a set of data specified using kwargs into `__into` using `__data` as input."""
    if not is_dataclass(__into):
        raise ValueError("__into must be a dataclass")

    attrs = {}
    for attr, path in kwargs.items():
        type_of_attr = __into.__annotations__[attr]
        attrs[attr] = path._pluck(__data, type_of_attr)

    print(attrs)

    return __into(**attrs)  # type: ignore[call-arg]

from typing import Union, Callable, Any

JSONStructure = Union[list, dict]
JSONValue = Union[str, int, float, JSONStructure]
MapperFn = Callable[[Any], Any]
Mapper = Union[MapperFn, dict]

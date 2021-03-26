from typing import Union, Callable, Any

JSONStructure = Union[list, dict]
JSONValue = Union[str, int, float, JSONStructure]
Mapper = Union[Callable[[Any], Any], dict]

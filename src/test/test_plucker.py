import pytest
from typing import List
from dataclasses import dataclass
from ..plucker import pluck, Path, PluckError


def test_plucking_basic():
    @dataclass
    class Struct:
        state_from: str
        state_to: str
        ids: List[int]
        num: int

    json = {
        "number": 3,
        "payload": {
            "from": "M",
            "to": "R",
            "who": [
                {"id": 12, "name": "X"},
                {"id": 41, "name": "Y"},
                {"id": 55, "name": "Z"},
            ],
        },
    }

    assert (
        pluck(
            json,
            Struct,
            num=Path(".number"),
            state_from=Path(".payload.from"),
            state_to=Path(".payload.to"),
            ids=Path(".payload.who[].id"),
        )
        == Struct(num=3, state_from="M", state_to="R", ids=[12, 41, 55])
    )


def test_list_when_basic_type_expected():
    @dataclass
    class Struct:
        value: int

    json = {"dictionary": {"fred": [2]}}

    with pytest.raises(PluckError) as exc_info:
        pluck(
            json,
            Struct,
            value=Path(".dictionary.fred"),
        )

    assert ".dictionary.fred should be 'int' but is 'list' instead" in str(
        exc_info.value
    )


def test_typed_name_checking():
    @dataclass
    class Struct:
        value: str

    json = {"number": 123}

    with pytest.raises(PluckError) as exc_info:
        pluck(
            json,
            Struct,
            value=Path(".number"),
        )

    assert ".number should be 'str' but is 'int' instead" in str(exc_info.value)


def test_typed_array_checking():
    @dataclass
    class Struct:
        ids: List[int]

    json = {
        "who": [
            {"id": 12, "name": "X"},
            {"id": "41", "name": "Y"},
            {"id": 55, "name": "Z"},
        ],
    }

    with pytest.raises(PluckError) as exc_info:
        pluck(
            json,
            Struct,
            ids=Path(".who[].id"),
        )

    assert ".who[1].id should be 'int' but is 'str' instead" in str(exc_info.value)


def test_dictionary_mapping():
    @dataclass
    class Struct:
        value: int

    mapping = {"RED": 2}
    json = {"value": "RED"}

    assert (
        pluck(
            json,
            Struct,
            value=Path(".value").map(mapping),
        )
        == Struct(2)
    )


def test_failed_dictionary_mapping():
    @dataclass
    class Struct:
        value: int

    mapping = {"GREEN": 3}
    json = {"value": "RED"}

    with pytest.raises(PluckError) as exc_info:
        pluck(
            json,
            Struct,
            value=Path(".value").map(mapping),
        )

    assert "Couldn't map .value (value is 'RED')" in str(exc_info.value)


def test_function_mapping():
    @dataclass
    class Struct:
        length: int

    json = {"value": [1, 2, 3, 4]}

    assert (
        pluck(
            json,
            Struct,
            length=Path(".value").map(len),
        )
        == Struct(4)
    )


def test_failed_function_mapping():
    @dataclass
    class Struct:
        length: int

    json = {"value": [1, 2, 3, 4]}

    with pytest.raises(PluckError) as exc_info:
        pluck(
            json,
            Struct,
            length=Path(".value").map(int),
        )

    assert "Couldn't map .value (value is [1, 2, 3, 4])" in str(exc_info.value)

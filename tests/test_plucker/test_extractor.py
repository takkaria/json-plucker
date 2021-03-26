import pytest
from typing import List

from plucker.types import JSONValue
from plucker.extractor import extract, _get_from_path, ExtractError
from plucker.tokeniser import ArrayToken, NameToken, Range, Token


# A fake range cos it doesn't really matter.
fr = Range(0, 0)


def test_getter():
    data = {"fred": 2}
    path: List[Token] = [NameToken(fr, "fred")]
    assert _get_from_path(data, path) == 2


def test_getter_array():
    data = {"fred": [2, 3, 4]}
    path: List[Token] = [NameToken(fr, "fred")]
    assert _get_from_path(data, path) == [2, 3, 4]


def test_getter_array_subs():
    data = {"fred": [{"v": 2}, {"v": 3}]}
    path: List[Token] = [NameToken(fr, "fred"), ArrayToken(fr), NameToken(fr, "v")]
    assert _get_from_path(data, path) == [2, 3]


def test_getter_array_sub_subs():
    data = [
        {"fred": [{"v": 2}, {"v": 3}]},
        {"fred": [{"v": 2}, {"v": 3}]},
    ]
    path: List[Token] = [
        ArrayToken(fr),
        NameToken(fr, "fred"),
        ArrayToken(fr),
        NameToken(fr, "v"),
    ]
    assert _get_from_path(data, path) == [[2, 3], [2, 3]]


def test_getter_array_error():
    data: JSONValue = [
        {"fred": []},
        {"fred": []},
    ]
    path = ".fred[].v"
    with pytest.raises(ExtractError) as exc:
        extract(data, path)

    assert "expected fred to be 'dict' but it was 'list'" in str(exc)

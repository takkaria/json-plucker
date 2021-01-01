from . import get_from_path
from .tokeniser import ArrayToken, NameToken

import pytest


def test_getter():
    data = {"fred": 2}
    path = [NameToken("fred")]
    assert get_from_path(data, path) == 2


def test_getter_array():
    data = {"fred": [2, 3, 4]}
    path = [NameToken("fred")]
    assert get_from_path(data, path) == [2, 3, 4]


def test_getter_array_subs():
    data = {"fred": [{"v": 2}, {"v": 3}]}
    path = [NameToken("fred"), ArrayToken(), NameToken("v")]
    assert get_from_path(data, path) == [2, 3]


def test_getter_array_sub_subs():
    data = [
        {"fred": [{"v": 2}, {"v": 3}]},
        {"fred": [{"v": 2}, {"v": 3}]},
    ]
    path = [ArrayToken(), NameToken("fred"), ArrayToken(), NameToken("v")]
    assert get_from_path(data, path) == [[2, 3], [2, 3]]


def test_getter_array_sub_subs():
    data = [
        {"fred": [{"v": 2}, {"v": 3}]},
        {"fred": [{"v": 2}, {"v": 3}]},
    ]
    path = [ArrayToken(), NameToken("fred"), ArrayToken(), NameToken("v")]
    assert get_from_path(data, path) == [[2, 3], [2, 3]]


def test_getter_array_sub_subs():
    data = [
        {"fred": [{"v": 2}, {"v": 3}]},
        {"fred": [{"v": 2}, {"v": 3}]},
    ]
    path = [NameToken("fred"), ArrayToken(), NameToken("v")]
    with pytest.raises(ValueError) as exc:
        get_from_path(data, path)

    breakpoint()

import pytest
from .tokeniser import tokenise, ArrayToken, NameToken


def test_minimal():
    assert tokenise(".") == []


def test_name():
    assert tokenise(".fred") == [NameToken("fred")]


def test_root_array():
    assert tokenise(".[]") == [ArrayToken()]


def test_name_then_array():
    assert tokenise(".names[]") == [NameToken("names"), ArrayToken()]


def test_name_then_array_then_name_then_array():
    assert tokenise(".names[].freddo[]") == [
        NameToken("names"),
        ArrayToken(),
        NameToken("freddo"),
        ArrayToken(),
    ]


def test_no_initial_dot():
    with pytest.raises(ValueError):
        tokenise("name")


def test_incomplete_array():
    with pytest.raises(ValueError):
        tokenise(".[")

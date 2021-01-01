import pytest
from ..tokeniser import tokenise, ArrayToken, NameToken, Range


def test_minimal():
    assert tokenise(".") == []


def test_name_only():
    assert tokenise(".fred") == [NameToken(Range(1, 5), "fred")]


def test_root_array():
    assert tokenise(".[]") == [ArrayToken(Range(1, 3))]


def test_name_then_array():
    assert tokenise(".names[]") == [
        NameToken(Range(1, 6), "names"),
        ArrayToken(Range(6, 8)),
    ]

    assert ".names[]"[1:6] == "names"
    assert ".names[]"[6:8] == "[]"


def test_name_then_array_then_name_then_array():
    assert tokenise(".names[].freddo[]") == [
        NameToken(Range(1, 6), "names"),
        ArrayToken(Range(6, 8)),
        NameToken(Range(9, 15), "freddo"),
        ArrayToken(Range(15, 17)),
    ]


def test_no_initial_dot():
    with pytest.raises(ValueError):
        tokenise("name")


def test_incomplete_array():
    with pytest.raises(ValueError):
        tokenise(".[")


def test_tokeniser_locations_are_correct():
    path = ".names[].freddo[]"
    tokens = tokenise(path)

    last = 0
    out = ""
    for t in tokens:
        if isinstance(t, NameToken):
            s = "n"
        elif isinstance(t, ArrayToken):
            s = "*"

        if t.location.start > last:
            out += " " * (t.location.start - last)

        out += s * len(t.location)

        last = t.location.end

    assert out == " nnnnn** nnnnnn**"

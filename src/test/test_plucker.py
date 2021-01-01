from typing import List
from dataclasses import dataclass
from ..plucker import pluck, Path


def test_plucking_basic():
    @dataclass
    class StatusChange:
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
            StatusChange,
            num=Path(".number"),
            state_from=Path(".payload.from"),
            state_to=Path(".payload.to"),
            ids=Path(".payload.who[].id"),
        )
        == StatusChange(num=3, state_from="M", state_to="R", ids=[12, 41, 55])
    )

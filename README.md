Existing ways to do this:
1. Are not type safe (DRF)
2. Require the same structure between the JSON and the serialization (dataclasses_json)


payload:

```json
{
    "date": "2020-12-12",
    "type": "membership:statuschange",
    "number_as_str": "2",
    "payload": {
        "from": "CURRENT",
        "to": "EXPIRED",
        "who": [
            { "name": "Fred Whelks", id: 102 },
            { "name": "Fisher Carrie", id: 1334 }
        ]
    },
    "from": "Hub <bef34acb948f>"
}
```


Nice things about this library:

* Simple syntax
* Good error messages

```
Data not in expected format; expected fred to be 'dict' but it was 'list':
.fred[].v
 ^^^^
```

Example:


```python
from typing import List
from enum import Enum, auto
from dataclasses import dataclass
from datetime import date
from plucker import pluck, Path


class MemberStatus(Enum):
    CURRENT = auto()
    EXPIRED = auto()


TO_STATUS = {"CUR": MemberStatus.CURRENT, "EXP": MemberStatus.EXPIRED}


@dataclass
class Person:
    name: str
    id: int


@dataclass
class StatusChange:
    date: date
    state_from: MemberStatus
    state_to: MemberStatus
    ids: List[int]
    num: int


def get(json: dict) -> StatusChange:
    return pluck(
        json,
        StatusChange,
        date=Path(".date"),
        num=Path(".number_as_str").map(int),
        state_from=Path(".payload.from").map(TO_STATUS),
        state_to=Path(".payload.to").map(TO_STATUS),
        ids=Path(".payload.who[].id"),
        people=Path(".payload.who[]").into(
            Person,
            name=Path(".name"),
            id=Path(".id"),
        ),
    )
```

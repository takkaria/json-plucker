# `plucker`

[![Build Status](https://github.com/takkaria/plucker/workflows/test/badge.svg?branch=master&event=push)](https://github.com/takkaria/plucker/actions?query=workflow%3Atest)
[![codecov](https://codecov.io/gh/takkaria/plucker/branch/master/graph/badge.svg)](https://codecov.io/gh/takkaria/plucker)
[![Python Version](https://img.shields.io/pypi/pyversions/plucker.svg)](https://pypi.org/project/plucker/)

Validate and extract JSON-sourced data into type-safe dataclasses


## wut

* Tired of relying on vendor-provided, untyped Python libraries to interface with external APIs?
* Want to just make a few simple HTTP requests without the weight of extra dependencies?
* Do you only use a small subset of the data you get from external sources, picking out five fields when you are given thirty?
* Are you more than slightly worried that the API might change under you and you wouldn't know?
* Want to avoid just reaching into dictionaries to get the data you want?
* Do you want to parse the JSON you get into something type-safe so that mypy will complain when you do wrong things?
* Is writing fakes a bit too heavyweight for the APIs you're calling?  Would producing an error on unexpected input work OK for now?

Enter `plucker`.

`plucker` is designed to validate, map and reduce regularly structured data into `dataclass`es.  That data would typically be JSON from APIs but could be anything that mostly consists of Python dicts and lists when parsed.

`plucker` will either give you type-verified data, or it will fail with helpful error messages:

```
Data not in expected format; expected fred to be 'list' but it was 'dict':
.fred[].v
 ^^^^
```

Just pick the data you want using `jq`-style paths, map it so that it's the right type if you need to, and you have well-typed validated data to feed into the rest of your system.


## Installation (soon...)

```bash
pip install plucker
```


## Example



```python
from typing import List
from dataclasses import dataclass
from enum import Enum, auto
from datetime import date

from plucker import pluck, Path


class Status(Enum):
    """A cintact's status."""
    CURRENT = auto()
    EXPIRED = auto()


@dataclass
class Contact:
    """A contact record."""
    name: str
    email: str


@dataclass
class Struct:
    """The typed dataclass we want our data collected into."""
    date: date
    id: int
    state: Status
    affected_records: List[int]
    contacts: List[Contact]


TO_STATUS = {"CUR": Status.CURRENT, "EXP": Status.EXPIRED}

input_ = {
    "date": "2021-01-01",
    "id": "1242",
    "payload": {
        "from": "CURRENT",
        "who": [
            {"name": "DM", "id": 1, "email": "dangermouse@example.com"},
            {"name": "Stiletto", "id": 23, "email": "baroni@example.com"},
        ]
    }
}

plucked = pluck(
    input_,
    Struct,
    date=Path(".date"),
    id=Path(".id").map(int),
    state=Path(".payload.from").map(TO_STATUS),
    affected_records=Path(".payload.who[].id"),
    people=Path(".payload.who[]").into(
        Contact,
        name=Path(".name"),
        email=Path(".email"),
    ),
)

expected = Struct(
    date=date(2021, 1, 1),
    id=1242,
    state=Status.CURRENT,
    affected_records=[1, 23],
    contacts=[
        Contact("DM", "dangermouse@example.com"),
        Contact("Stiletto", "baroni@example.com")
    ]
)

assert plucked == expected
# ^ it's True
```


## Prior art

1. dataclasses_json -> require the same structure between JSON and serialization, which means you have to specify an intermediate structure
2. DRF serializers -> heavyweight and not type safe, destructure into dictionaries
3. Elm's JSON decoders -> this design isn't really based on anything in there but ever since using them I wanted similar functionality in Python
4. `jq`, an amazing commandline tool for querying JSON data
5. [Parse, don't validate](https://lexi-lambda.github.io/tags/functional-programming.html)
6. Elm's error messages


## License

[MIT](https://github.com/takkaria/plucker/blob/master/LICENSE)


## Credits

A bunch of the tooling was taken from [`wemake-python-package`](https://github.com/wemake-services/wemake-python-package) but then heavily modified.

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

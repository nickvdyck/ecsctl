from typing import Optional, TypedDict


class PlacementConstraint(TypedDict):
    type: Optional[str]
    expression: Optional[str]


class KeyValuePair(TypedDict):
    name: str
    value: str

from typing import Optional, TypedDict, Literal


class KeyValuePair(TypedDict):
    name: str
    value: str


class PlacementConstraint(TypedDict):
    type: Optional[str]
    expression: Optional[str]


# https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_EnvironmentFile.html
class EnvironmentFile(TypedDict):
    type: str
    value: str


class ResourceRequirement(TypedDict):
    type: Literal["GPU", "InferenceAccelerator"]
    value: str

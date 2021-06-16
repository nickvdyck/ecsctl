from dataclasses import dataclass
from ecsctl.models.common import KeyValuePair
from typing import Any, Dict, Literal, List


@dataclass(frozen=True)
class Cluster:
    DEFAULT_COLUMNS = [
        "name",
        "status",
        "instances",
        "services",
        "running_tasks",
        "pending_tasks",
    ]

    arn: str
    name: str
    status: str
    instances: int
    services: int
    running_tasks: int
    pending_tasks: int
    statistics: List[Any]
    settings: List[KeyValuePair]
    capacity_providers: List[Literal["FARGATE", "FARGATE_SPOT"]]
    default_capacity_provider_strategy: List[str]
    tags: Dict[str, str]

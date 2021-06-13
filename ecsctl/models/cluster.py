from ecsctl.models.common import KeyValuePair
from typing import Any, Dict, Literal, List


class Cluster:
    DEFAULT_COLUMNS = [
        "name",
        "status",
        "instances",
        "services",
        "running_tasks",
        "pending_tasks",
    ]

    def __init__(
        self,
        arn: str,
        name: str,
        status: str,
        instances: int,
        services: int,
        running_tasks: int,
        pending_tasks: int,
        statistics: List[Any],
        settings: List[KeyValuePair],
        capacity_providers: List[Literal["FARGATE", "FARGATE_SPOT"]],
        default_capacity_provider_strategy: List[str],
        tags: Dict[str, str],
    ):
        self.arn = arn
        self.name = name
        self.status = status
        self.instances = instances
        self.services = services
        self.running_tasks = running_tasks
        self.pending_tasks = pending_tasks
        self.statistics = statistics
        self.settings = settings
        self.capacity_providers = capacity_providers
        self.default_capacity_provider_strategy = default_capacity_provider_strategy
        self.tags = tags

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Instance:
    DEFAULT_COLUMNS = [
        "id",
        "ec2_instance_id",
        "status",
        "running_tasks",
        "pending_tasks",
        "registered_at",
    ]

    id: str
    arn: str
    ec2_instance_id: str
    status: str
    agent_connected: bool
    running_tasks: int
    pending_tasks: int
    agent_update_status: str
    registered_at: datetime

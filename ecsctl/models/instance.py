from datetime import datetime


class Instance:
    DEFAULT_COLUMNS = [
        "id",
        "ec2_instance",
        "status",
        "running_tasks",
        "pending_tasks",
        "registered_at",
    ]

    def __init__(
        self,
        arn: str,
        ec2_instance_id: str,
        status: str,
        agent_connected: bool,
        running_tasks: int,
        pending_tasks: int,
        agent_update_status: str,
        registered_at: datetime,
    ):
        self.id = arn.split("/")[-1]
        self.arg = arn
        self.ec2_instance = ec2_instance_id
        self.status = status
        self.agent_connected = agent_connected
        self.running_tasks = running_tasks
        self.pending_tasks = pending_tasks
        self.agent_update_status = agent_update_status
        self.registered_at = registered_at

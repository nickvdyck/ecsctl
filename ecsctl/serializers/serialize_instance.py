from typing import Any, Dict
from ecsctl.models import Instance


def deserialize_instance(instance: Dict[str, Any]) -> Instance:
    container_instance_arn = instance.get("containerInstanceArn", "")
    return Instance(
        container_instance_arn.split("/")[-1],
        container_instance_arn,
        instance["ec2InstanceId"],
        instance["status"],
        instance["agentConnected"],
        instance["runningTasksCount"],
        instance["pendingTasksCount"],
        instance.get("agentUpdateStatus", None),
        instance["registeredAt"],
    )


def serialize_instance(instance: Instance) -> Dict[str, Any]:
    return {
        "id": instance.id,
        "ec2_instance_id": instance.ec2_instance_id,
        "status": instance.status,
        "running_tasks": instance.running_tasks,
        "pending_tasks": instance.pending_tasks,
        "registered_at": instance.registered_at.isoformat(),
    }

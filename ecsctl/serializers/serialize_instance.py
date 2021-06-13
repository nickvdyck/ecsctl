from typing import Any, Dict
from ecsctl.models import Instance


def deserialize_instance(instance: Dict[str, Any]) -> Instance:
    return Instance(
        instance["containerInstanceArn"],
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
        "ec2_instance": instance.ec2_instance,
        "status": instance.status,
        "running_tasks": instance.running_tasks,
        "pending_tasks": instance.pending_tasks,
        "registered_at": instance.registered_at.isoformat(),
    }

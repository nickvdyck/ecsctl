from typing import Dict, Any
from ecsctl.models import Cluster, Instance, Service, ServiceEvent, Task


def serialize_ecs_cluster(cluster: Cluster) -> Dict[str, str]:
    return {
        "name": cluster.name,
        "status": cluster.status,
        "instances": cluster.status,
        "services": cluster.services,
        "running_tasks": cluster.running_tasks,
        "pending_tasks": cluster.pending_tasks,
    }


def deserialize_ecs_service(service: Dict[str, Any]) -> Service:
    return Service(
        service["serviceArn"],
        service["serviceName"],
        service["clusterArn"],
        service["status"],
        service["desiredCount"],
        service["runningCount"],
        service["pendingCount"],
        service["launchType"],
        service["taskDefinition"],
        service.get("roleArn", None),
        service["createdAt"],
        service.get("createdBy", None),
        service["schedulingStrategy"],
        [deserialize_ecs_service_events(event) for event in service.get("events", [])],
    )


def serialize_ecs_service(service: Service) -> Dict[str, Any]:
    return {
        "arn": service.arn,
        "name": service.name,
        "cluster_arn": service.cluster_arn,
        "status": service.status,
        "desired": service.desired,
        "running": service.running,
        "pending": service.pending,
        "type": service.type,
        "task_definition": service.task_definition,
        "role_arn": service.role_arn,
        "created_at": service.created_at.isoformat(),
        "created_by": service.created_by,
        "scheduling_strategy": service.scheduling_strategy,
    }


def deserialize_ecs_service_events(event: Dict[str, str]) -> ServiceEvent:
    return ServiceEvent(
        event["id"],
        event["createdAt"],
        event["message"],
    )


def deserialize_ecs_task(task: Dict[str, Any]) -> Task:
    return Task(
        task["taskArn"],
        task["taskDefinitionArn"],
        task["clusterArn"],
        task["containerInstanceArn"],
        task["availabilityZone"],
        task["connectivity"],
        task["connectivityAt"],
        task["createdAt"],
        task["lastStatus"],
        task["desiredStatus"],
        task["healthStatus"],
        task["launchType"],
        task["cpu"],
        task["memory"],
        task["group"],
        task["pullStartedAt"],
        task["pullStoppedAt"],
        task["startedAt"],
        task["startedBy"],
        task.get("stoppedAt", None),
        task.get("stoppedReason", ""),
        task["tags"],
    )


def serialize_ecs_task(task: Task) -> Dict[str, str]:
    task_json = {
        "id": task.id,
        "arn": task.arn,
        "task_definition": task.task_definition,
        "task_definition_arn": task.task_definition_arn,
        "cluster_arn": task.cluster_arn,
        "container_instance_id": task.container_instance_id,
        "container_instance_arn": task.container_instance_arn,
        "availability_zone": task.availability_zone,
        "connectivity": task.connectivity,
        "connectivity_at": task.connectivity_at.isoformat(),
        "created_at": task.created_at.isoformat(),
        "status": task.status,
        "desired_status": task.desired_status,
        "health": task.health,
        "type": task.type,
        "cpu": task.cpu,
        "memory": task.memory,
        "group": task.group,
        "pull_started_at": task.pull_started_at.isoformat(),
        "pull_stopped_at": task.pull_stopped_at.isoformat(),
        "started_at": task.started_at.isoformat(),
        "started_by": task.started_by,
        "stopped_reason": task.stopped_reason,
        "tags": task.tags,
    }

    if task.stopped_at is not None:
        task_json["stopped_at"] = task.stopped_at.isoformat()

    return task_json


def deserialize_ecs_instance(instance: Dict[str, Any]) -> Instance:
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


def serialize_ecs_instance(instance: Instance) -> Dict[str, Any]:
    return {
        "id": instance.id,
        "ec2_instance": instance.ec2_instance,
        "status": instance.status,
        "running_tasks": instance.running_tasks,
        "pending_tasks": instance.pending_tasks,
        "registered_at": instance.registered_at.isoformat(),
    }

from ecsctl.utils import filter_empty_values
from ecsctl.models.task import (
    ContainerOverride,
    InferenceAcceleratorOverride,
    TaskOverride,
)
from typing import Any, Dict
from ecsctl.models import (
    Attachment,
    Container,
    ManagedAgent,
    NetworkBinding,
    NetworkInterface,
    Task,
)


def deserialize_attachment(attachment: Dict[str, Any]) -> Attachment:
    return Attachment(
        attachment["id"],
        attachment["type"],
        attachment["status"],
        attachment.get("details", []),
    )


def serialize_attachment(attachment: Attachment) -> Dict[str, Any]:
    return {
        "id": attachment.id,
        "type": attachment.type,
        "status": attachment.status,
        "details": attachment.details,
    }


def deserialize_network_binding(binding: Dict[str, Any]) -> NetworkBinding:
    return NetworkBinding(
        binding["bindIP"],
        binding["containerPort"],
        binding["hostPort"],
        binding["protocol"],
    )


def serialize_network_binding(binding: NetworkBinding) -> Dict[str, Any]:
    return {
        "bind_ip": binding.bind_ip,
        "container_port": binding.container_port,
        "host_port": binding.host_port,
        "protocol": binding.protocol,
    }


def deserialize_network_interface(interface: Dict[str, Any]) -> NetworkInterface:
    return NetworkInterface(
        interface["attachmentId"],
        interface["privateIpv4Address"],
        interface.get("ipv6Address", None),
    )


def serialize_network_interface(interface: NetworkInterface) -> Dict[str, Any]:
    return {
        "attachment_id": interface.attachment_id,
        "ipv4_address": interface.ipv4_address,
        "ipv6_address": interface.ipv6_address,
    }


def deserialize_managed_agent(agent: Dict[str, Any]) -> ManagedAgent:
    return ManagedAgent(
        agent["name"],
        agent["reason"],
        agent["lastStatus"],
        agent["lastStartedAt"],
    )


def serialize_managed_agent(agent: ManagedAgent) -> Dict[str, Any]:
    return {
        "name": agent.name,
        "reason": agent.reason,
        "status": agent.status,
        "started_at": agent.started_at.isoformat(),
    }


def deserialize_container(container: Dict[str, Any]) -> Container:
    container_arn = container.get("containerArn", "")
    task_arn = container.get("taskArn", "")
    return Container(
        container_arn.split("/")[-1],
        container_arn,
        task_arn.split("/")[-1],
        task_arn,
        container["name"],
        container["image"],
        container.get("imageDigest", None),
        container.get("runtimeId", None),
        container["lastStatus"],
        container.get("exitCode", None),
        container.get("reason", ""),
        container["healthStatus"],
        container["cpu"],
        container.get("memory", None),
        container.get("memoryReservation", None),
        [
            deserialize_network_binding(binding)
            for binding in container.get("networkBindings", [])
        ],
        [
            deserialize_network_interface(interface)
            for interface in container.get("networkInterfaces", [])
        ],
        [
            deserialize_managed_agent(agent)
            for agent in container.get("managedAgents", [])
        ],
        container.get("gpuIds", []),
    )


def serialize_container(container: Container) -> Dict[str, Any]:
    json = {
        "id": container.id,
        "task_arn": container.arn,
        "name": container.name,
        "image": container.image,
        "runtime_id": container.runtime_id,
        "status": container.status,
        "exit_code": container.exit_code,
        "reason": container.reason,
        "health": container.health,
        "cpu": container.cpu,
        "memory": container.memory,
        "memory_reservation": container.memory_reservation,
        "network_bindings": [
            serialize_network_binding(binding) for binding in container.network_bindings
        ],
        "network_interfaces": [
            serialize_network_interface(interface)
            for interface in container.network_interfaces
        ],
        "managed_agents": [
            serialize_managed_agent(agent) for agent in container.managed_agents
        ],
        "gpu_ids": container.gpu_ids,
    }

    if container.image_digest is not None:
        json["image_digest"] = container.image_digest

    return json


def deserialize_container_overrides(override: Dict[str, Any]) -> ContainerOverride:
    return ContainerOverride(
        override.get("name", None),
        override.get("command", None),
        override.get("cpu", None),
        override.get("memory", None),
        override.get("memoryReservation", None),
        override.get("environment", None),
        override.get("environmentFiles", None),
        override.get("resourceRequirements", None),
    )


def serialize_container_overrides(override: ContainerOverride) -> Dict[str, Any]:
    json = {
        "name": override.name,
        "command": override.command,
        "cpu": override.cpu,
        "memory": override.memory,
        "memory_reservation": override.memory_reservation,
        "environment": override.environment,
        "environment_files": override.environment_files,
        "resource_requirements": override.resource_requirements,
    }
    return filter_empty_values(json)


def deserialize_inference_accelerator_override(
    override: Dict[str, Any]
) -> InferenceAcceleratorOverride:
    return InferenceAcceleratorOverride(
        override.get("deviceName", None), override.get("deviceType", None)
    )


def serialize_inference_accelerator_override(
    override: InferenceAcceleratorOverride,
) -> Dict[str, Any]:
    json = {"device_name": override.device_name, "device_type": override.device_type}

    return filter_empty_values(json)


def deserialize_task_override(task_override: Dict[str, Any]) -> TaskOverride:
    container_overrides = task_override.get("containerOverrides", None)
    inference_overrides = task_override.get("inferenceAcceleratorOverrides", None)
    return TaskOverride(
        [deserialize_container_overrides(override) for override in container_overrides]
        if container_overrides is not None
        else None,
        task_override.get("cpu", None),
        [
            deserialize_inference_accelerator_override(override)
            for override in inference_overrides
        ]
        if container_overrides is not None
        else None,
    )


def serialize_task_override(task_override: TaskOverride) -> Dict[str, Any]:
    json = {
        "container_overrides": [
            serialize_container_overrides(override)
            for override in task_override.container_overrides
        ]
        if task_override.container_overrides is not None
        else None,
        "cpu": task_override.cpu,
        "inference_accelerator_overrides": [
            serialize_inference_accelerator_override(override)
            for override in task_override.inference_accelerator_overrides
        ]
        if task_override.inference_accelerator_overrides is not None
        else None,
    }

    return filter_empty_values(json)


def deserialize_task(task: Dict[str, Any]) -> Task:
    arn = task.get("taskArn", "")
    task_definition_arn = task.get("taskDefinitionArn", "")
    launch_type = task.get("launchType", None)
    container_instance_arn = task.get("containerInstanceArn", "")
    overrides = task.get("overrides", None)

    if launch_type == "EC2":
        container_instance_id = container_instance_arn.split("/")[-1]
        container_instance_arn = container_instance_arn
    else:
        container_instance_id = None
        container_instance_arn = None

    return Task(
        arn.split("/")[-1],
        arn,
        task_definition_arn.split("/")[-1],
        task_definition_arn,
        task["clusterArn"],
        container_instance_id,
        container_instance_arn,
        task["availabilityZone"],
        task.get("connectivity", None),
        task.get("connectivityAt", None),
        task["createdAt"],
        task["lastStatus"],
        task["desiredStatus"],
        task["healthStatus"],
        task["launchType"],
        task.get("enableExecuteCommand", False),
        task["cpu"],
        task["memory"],
        task["group"],
        task.get("pullStartedAt", None),
        task.get("pullStoppedAt", None),
        task.get("startedAt", None),
        task.get("startedBy", None),
        task.get("stoppedAt", None),
        task.get("stoppedReason", ""),
        task["tags"],
        [deserialize_container(container) for container in task["containers"]],
        [
            deserialize_attachment(attachment)
            for attachment in task.get("attachments", [])
        ],
        deserialize_task_override(overrides) if overrides is not None else None,
    )


def serialize_task(task: Task) -> Dict[str, str]:
    task_json = {
        "id": task.id,
        "arn": task.arn,
        "task_definition": task.task_definition,
        "task_definition_arn": task.task_definition_arn,
        "cluster_arn": task.cluster_arn,
        "availability_zone": task.availability_zone,
        "connectivity": task.connectivity,
        "connectivity_at": task.connectivity_at.isoformat()
        if task.connectivity_at is not None
        else None,
        "created_at": task.created_at.isoformat()
        if task.created_at is not None
        else None,
        "status": task.status,
        "desired_status": task.desired_status,
        "health": task.health,
        "launch_type": task.launch_type,
        "enable_execute_command": task.enable_execute_command,
        "cpu": task.cpu,
        "memory": task.memory,
        "group": task.group,
        "pull_started_at": task.pull_started_at.isoformat()
        if task.pull_started_at is not None
        else None,
        "pull_stopped_at": task.pull_stopped_at.isoformat()
        if task.pull_stopped_at is not None
        else None,
        "started_at": task.started_at.isoformat()
        if task.started_at is not None
        else None,
        "started_by": task.started_by,
        "stopped_reason": task.stopped_reason,
        "stopped_at": task.stopped_at.isoformat()
        if task.stopped_at is not None
        else None,
        "tags": task.tags,
        "attachments": [
            serialize_attachment(attachment) for attachment in task.attachments
        ],
        "overrides": serialize_task_override(task.overrides)
        if task.overrides is not None
        else None,
    }

    if task.launch_type == "ECS":
        task_json["container_instance_id"] = task.container_instance_id
        task_json["container_instance_arn"] = task.container_instance_arn

    return filter_empty_values(task_json)

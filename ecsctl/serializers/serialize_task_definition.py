from ecsctl.utils import filter_empty_values
from ecsctl.models import (
    ContainerDefinition,
    HealthCheck,
    LogConfiguration,
    MountPoint,
    Secret,
    VolumeFrom,
    TaskDefinition,
)
from typing import Any, Dict, Optional


def deserialize_secret(secret: Dict[str, Any]) -> Secret:
    return Secret(name=secret["name"], value_from=secret["valueFrom"])


def serialize_secret(secret: Secret) -> Dict[str, Any]:
    return {
        "name": secret.name,
        "value_from": secret.value_from,
    }


def deserialize_volume_from(volume_from: Dict[str, Any]) -> VolumeFrom:
    return VolumeFrom(
        read_only=volume_from["readOnly"],
        source_container=volume_from["sourceContainer"],
    )


def serialize_volume_from(volume_form: VolumeFrom) -> Dict[str, Any]:
    return {
        "read_only": volume_form.read_only,
        "source_container": volume_form.source_container,
    }


def deserialize_mount_point(mount_point: Dict[str, Any]) -> MountPoint:
    return MountPoint(
        container_path=mount_point["containerPath"],
        read_only=mount_point["readOnly"],
        source_volume=mount_point["sourceVolume"],
    )


def serialize_mount_point(mount_point: MountPoint) -> Dict[str, Any]:
    return {
        "container_path": mount_point.container_path,
        "read_only": mount_point.read_only,
        "source_volume": mount_point.source_volume,
    }


def deserialize_log_configuration(
    log_config: Optional[Dict[str, Any]]
) -> Optional[LogConfiguration]:
    if log_config is None:
        return None

    return LogConfiguration(
        log_driver=log_config["logDriver"],
        options=log_config.get("options", {}),
        secret_options=log_config.get("secretOptions", None),
    )


def serialize_log_configuration(
    log_config: Optional[LogConfiguration],
) -> Optional[Dict[str, Any]]:
    if log_config is None:
        return None

    return {
        "log_driver": log_config.log_driver,
        "options": log_config.options,
        "secret_options": log_config.secret_options,
    }


def deserialize_health_check(health: Optional[Dict[str, Any]]) -> Optional[HealthCheck]:
    if health is None:
        return None

    return HealthCheck(
        command=health["command"],
        interval=health["interval"],
        timeout=health["timeout"],
        retries=health["retries"],
        start_period=health["startPeriod"],
    )


def serialize_health_check(health: Optional[HealthCheck]) -> Optional[Dict[str, Any]]:
    if health is None:
        return None

    return {
        "command": health.command,
        "interval": health.interval,
        "timeout": health.timeout,
        "retries": health.retries,
        "start_period": health.start_period,
    }


def deserialize_container_definition(definition: Dict[str, Any]) -> ContainerDefinition:
    return ContainerDefinition(
        name=definition["name"],
        image=definition["image"],
        cpu=definition.get("cpu", None),
        memory=definition.get("memory", None),
        memory_reservation=definition.get("memoryReservation", None),
        port_mappings=definition["portMappings"],
        essential=definition["essential"],
        environment=definition.get("environment", {}),
        mount_points=[
            deserialize_mount_point(mpoint)
            for mpoint in definition.get("mountPoint", [])
        ],
        volumes_from=[
            deserialize_volume_from(volume)
            for volume in definition.get("volumeFrom", [])
        ],
        secrets=[deserialize_secret(secret) for secret in definition.get("secret", [])],
        docker_labels=definition.get("dockerLabels", {}),
        health_check=deserialize_health_check(definition.get("healthCheck", None)),
        log_configuration=deserialize_log_configuration(
            definition.get("logConfiguration", None)
        ),
        linux_parameters=definition.get("linuxParameters", None),
    )


def serialize_container_defintion(definition: ContainerDefinition) -> Dict[str, Any]:
    json_dict = {
        "name": definition.name,
        "image": definition.image,
        "cpu": definition.cpu,
        "memory": definition.memory,
        "memory_reservation": definition.memory_reservation,
        "port_mappings": definition.port_mappings,
        "essential": definition.essential,
        "environment": definition.environment,
        "mount_points": [
            serialize_mount_point(point) for point in definition.mount_points
        ],
        "volumes_from": [
            serialize_volume_from(volume) for volume in definition.volumes_from
        ],
        "secrets": [serialize_secret(secret) for secret in definition.secrets],
        "docker_labels": definition.docker_labels,
        "health_check": serialize_health_check(definition.health_check),
        "log_configuration": serialize_log_configuration(definition.log_configuration),
        "linux_parameters": definition.linux_parameters,
    }

    return filter_empty_values(json_dict)


def deserialize_task_definition(definition: Dict[str, Any]):
    return TaskDefinition(
        arn=definition["taskDefinitionArn"],
        container_definitions=[
            deserialize_container_definition(c_def)
            for c_def in definition.get("containerDefinitions", [])
        ],
        family=definition["family"],
        task_role_arn=definition["taskRoleArn"],
        execution_role_arn=definition["executionRoleArn"],
        network_mode=definition["networkMode"],
        revision=definition["revision"],
        status=definition["status"],
        requires_attributes=definition.get("requiresAttributes", []),
        placement_constraints=definition.get("placementConstraints", []),
        compatibilities=definition.get("compatibilities"),
        requires_compatibilities=definition.get("requiresCompatibilities", []),
        registered_at=definition["registeredAt"],
        registered_by=definition["registeredBy"],
        deregistered_at=definition.get("deregisteredAt", None),
        deregistered_by=definition.get("deregisteredBy", None),
    )


def serialize_task_definition(definition: TaskDefinition) -> Dict[str, Any]:
    json_dict = {
        "arn": definition.arn,
        "container_definitions": [
            serialize_container_defintion(container)
            for container in definition.container_definitions
        ],
        "family": definition.family,
        "task_role_arn": definition.task_role_arn,
        "execution_role_arn": definition.execution_role_arn,
        "network_mode": definition.network_mode,
        "revision": definition.revision,
        "status": definition.status,
        "requires_attributes": definition.requires_attributes,
        "placement_constraints": definition.placement_constraints,
        "compatibilities": definition.compatibilities,
        "requires_compatibilities": definition.requires_compatibilities,
        "registered_at": definition.registered_at.isoformat(),
        "registered_by": definition.registered_by,
        "deregistered_at": definition.deregistered_at.isoformat()
        if definition.deregistered_at is not None
        else None,
        "deregistered_by": definition.deregistered_by,
    }

    return filter_empty_values(json_dict)

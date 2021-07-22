from dataclasses import dataclass

from datetime import datetime
from ecsctl.models.common import PlacementConstraint, KeyValuePair
from typing import Any, Dict, Literal, List, Optional, TypedDict


class PortMapping(TypedDict):
    container_port: int
    host_port: int
    protocol: str


@dataclass(frozen=True)
class Secret:
    __slots__ = ("name", "value_from")
    name: str
    value_from: str


@dataclass(frozen=True)
class MountPoint:
    __slots__ = ("container_path", "read_only", "source_volume")
    container_path: str
    read_only: bool
    source_volume: str


@dataclass(frozen=True)
class VolumeFrom:
    __slots__ = ("read_only", "source_container")
    read_only: bool
    source_container: str


@dataclass(frozen=True)
class LogConfiguration:
    __slots__ = ("log_driver", "options", "secret_options")
    log_driver: str
    options: Dict[str, str]
    secret_options: Optional[List[Secret]]


@dataclass(frozen=True)
class HealthCheck:
    __slots__ = ("command", "interval", "timeout", "retries", "start_period")
    command: List[str]
    interval: int
    timeout: int
    retries: int
    start_period: int


@dataclass(frozen=True)
class ContainerDefinition:
    name: str
    image: str
    entrypoint: Optional[List[str]]
    command: Optional[List[str]]
    cpu: Optional[int]
    memory: Optional[int]
    memory_reservation: Optional[int]
    port_mappings: List[PortMapping]
    essential: bool
    environment: List[KeyValuePair]
    mount_points: List[MountPoint]
    volumes_from: List[VolumeFrom]
    secrets: List[Secret]
    docker_labels: Dict[str, str]
    health_check: HealthCheck
    log_configuration: Optional[LogConfiguration]
    linux_parameters: Optional[Dict[str, Any]]


class RequiresAttribute(TypedDict):
    name: str


@dataclass(frozen=True)
class TaskDefinition:
    DEFAULT_COLUMNS = [
        "arn",
        "family",
        "revision",
        "status",
        "network_mode",
        "registered_at",
    ]

    arn: str
    container_definitions: List[ContainerDefinition]
    family: str
    task_role_arn: str
    execution_role_arn: str
    network_mode: Literal["none", "bridge", "awsvpc", "host"]
    revision: int
    status: str
    requires_attributes: List[RequiresAttribute]
    placement_constraints: List[PlacementConstraint]
    compatibilities: List[Literal["EXTERNAL", "EC2", "FARGATE"]]
    requires_compatibilities: List[Literal["EXTERNAL", "EC2", "FARGATE"]]
    registered_at: datetime
    registered_by: str
    deregistered_at: Optional[datetime]
    deregistered_by: Optional[str]

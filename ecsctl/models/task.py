from dataclasses import dataclass
from datetime import datetime
from typing import Literal, List, Optional, Union

from ecsctl.models.common import KeyValuePair


@dataclass(frozen=True)
class Attachment:
    __slots__ = ("id", "type", "status", "details")
    id: str
    type: str
    status: Literal["PRECREATED", "CREATED", "ATTACHING", "ATTACHED", "DETACHING", "DETACHED", "DELETED"]
    details: List[KeyValuePair]


@dataclass(frozen=True)
class NetworkBinding:
    __slots__ = ("bind_ip", "container_port", "host_port", "protocol")
    bind_ip: str
    container_port: int
    host_port: int
    protocol: Literal["tcp", "udp"]


@dataclass(frozen=True)
class NetworkInterface:
    __slots__ = ("attachment_id", "ipv4_address", "ipv6_address")
    attachment_id: str
    ipv4_address: str
    ipv6_address: str


@dataclass(frozen=True)
class ManagedAgent:
    __slots__ = ("name", "reason", "status", "started_at")
    name: str
    reason: str
    status: str
    started_at: datetime


@dataclass(frozen=True)
class Container:
    DEFAULT_COLUMNS = [
        "id",
        "name",
        "image",
        "health",
        "status",
        "exit_code",
        "reason",
    ]

    id: str
    arn: str
    task_id: str
    task_arn: str
    name: str
    image: str
    image_digest: str
    runtime_id: str
    status: str
    exit_code: int
    reason: str
    health: Literal["HEALTHY", "UNHEALTHY", "UNKNOWN"]
    cpu: int
    memory: int
    memory_reservation: int
    network_bindings: List[NetworkBinding]
    network_interfaces: List[NetworkInterface]
    managed_agents: List[ManagedAgent]
    gpu_ids: List[str]


@dataclass(frozen=True)
class Task:
    DEFAULT_COLUMNS = [
        "id",
        "task_definition",
        "status",
        "health",
        "container_instance_id",
        "started_at",
        "stopped_at",
        "stopped_reason",
    ]

    id: str
    arn: str
    task_definition: str
    task_definition_arn: str
    cluster_arn: str
    container_instance_id: Optional[str]
    container_instance_arn: Optional[str]
    availability_zone: str
    connectivity: Literal["CONNECTED", "DISCONNECTED"]
    connectivity_at: datetime
    created_at: datetime
    status: Literal[
        "PROVISIONING",
        "ACTIVATING",
        "RUNNING",
        "DEPROVISIONING",
        "DEACTIVATING",
        "STOPPED",
    ]
    desired_status: str
    health: Literal["HEALTHY", "UNHEALTHY", "UNKNOWN"]
    launch_type: Literal["EC2", "FARGATE", "EXTERNAL"]
    enable_execute_command: bool
    cpu: int
    memory: int
    group: str
    pull_started_at: datetime
    pull_stopped_at: datetime
    started_at: datetime
    started_by: str
    stopped_at: Union[datetime, None]
    stopped_reason: str
    tags: List[str]
    containers: List[Container]
    attachments: List[Attachment]

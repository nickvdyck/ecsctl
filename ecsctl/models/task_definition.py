from datetime import datetime
from ecsctl.models.common import PlacementConstraint, KeyValuePair
from typing import Any, Dict, Literal, List, Optional, TypedDict


class PortMapping(TypedDict):
    container_port: int
    host_port: int
    protocol: str


class Secret:
    def __init__(self, name: str, value_from: str):
        self.name = name
        self.value_from = value_from


class MountPoint:
    def __init__(self, container_path: str, read_only: bool, source_volume: str):
        self.container_path = container_path
        self.read_only = read_only
        self.source_volume = source_volume


class VolumeFrom:
    def __init__(self, read_only: bool, source_container: str):
        self.read_only = read_only
        self.source_container = source_container


class LogConfiguration:
    EMPTY: Any

    def __init__(
        self,
        log_driver: str,
        options: Dict[str, str],
        secret_options: Optional[List[Secret]],
    ):
        self.log_driver = log_driver
        self.options = options
        self.secret_options = secret_options


LogConfiguration.EMPTY = LogConfiguration("", {}, [])


class HealthCheck:
    EMPTY: Any

    def __init__(
        self,
        command: List[str],
        interval: int,
        timeout: int,
        retries: int,
        start_period: int,
    ):
        self.command = command
        self.interval = interval
        self.timeout = timeout
        self.retries = retries
        self.start_period = start_period


HealthCheck.EMPTY = HealthCheck([], 0, 0, 0, 0)


class ContainerDefinition:
    def __init__(
        self,
        name: str,
        image: str,
        cpu: Optional[int],
        memory: Optional[int],
        memory_reservation: Optional[int],
        port_mappings: List[PortMapping],
        essential: bool,
        environment: List[KeyValuePair],
        mount_points: List[MountPoint],
        volumes_from: List[VolumeFrom],
        secrets: List[Secret],
        docker_labels: Dict[str, str],
        health_check: HealthCheck,
        log_configuration: Optional[LogConfiguration] = None,
        linux_parameters: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.image = image
        self.cpu = cpu
        self.memory = memory
        self.memory_reservation = memory_reservation
        self.port_mappings = port_mappings
        self.essential = essential
        self.environment = environment
        self.mount_points = mount_points
        self.volumes_from = volumes_from
        self.secrets = secrets
        self.docker_labels = docker_labels
        self.health_check = health_check
        self.log_configuration = log_configuration
        self.linux_parameters = linux_parameters


class RequiresAttribute(TypedDict):
    name: str


class TaskDefinition:
    DEFAULT_COLUMNS = [
        "arn",
        "family",
        "revision",
        "status",
        "network_mode",
        "registered_at",
    ]

    def __init__(
        self,
        arn: str,
        container_definitions: List[ContainerDefinition],
        family: str,
        task_role_arn: str,
        execution_role_arn: str,
        network_mode: Literal["none", "bridge", "awsvpc", "host"],
        revision: int,
        status: str,
        requires_attributes: List[RequiresAttribute],
        placement_constraints: List[PlacementConstraint],
        compatibilities: List[Literal["EXTERNAL", "EC2", "FARGATE"]],
        requires_compatibilities: List[Literal["EXTERNAL", "EC2", "FARGATE"]],
        registered_at: datetime,
        registered_by: str,
        deregistered_at: Optional[datetime],
        deregistered_by: Optional[str],
    ):
        self.arn = arn
        self.container_definitions = container_definitions
        self.family = family
        self.task_role_arn = task_role_arn
        self.execution_role_arn = execution_role_arn
        self.network_mode = network_mode
        self.revision = revision
        self.status = status
        self.requires_attributes = requires_attributes
        self.placement_constraints = placement_constraints
        self.compatibilities = compatibilities
        self.requires_compatibilities = requires_compatibilities
        self.registered_at = registered_at
        self.registered_by = registered_by
        self.deregistered_at = deregistered_at
        self.deregistered_by = deregistered_by

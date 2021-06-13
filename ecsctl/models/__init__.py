from typing import Dict, List, Literal, Optional, TypedDict, Union
from datetime import datetime
from ecsctl.models.common import PlacementConstraint

from ecsctl.models.task_definition import *
from ecsctl.models.cluster import *


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


class Event:
    DEFAULT_COLUMNS = [
        "id",
        "created_at",
        "message",
    ]

    def __init__(self, _id: str, created_at: datetime, message: str):
        self.id = _id
        self.created_at = created_at
        self.message = message


class Deployment:
    DEFAULT_COLUMNS = [
        "id",
        "status",
        "desired",
        "pending",
        "running",
        "failed",
        "created_at",
        "rollout_state_reason",
    ]

    def __init__(
        self,
        _id: str,
        status: str,
        task_definition: str,
        desired: int,
        pending: int,
        running: int,
        failed: int,
        created_at: datetime,
        updated_at: datetime,
        launch_type: str,
        rollout_sate: str,
        rollout_state_reason: str,
    ):
        self.id = _id
        self.status = status
        self.task_definition = task_definition
        self.desired = desired
        self.pending = pending
        self.running = running
        self.failed = failed
        self.created_at = created_at
        self.updated_at = updated_at
        self.launch_type = launch_type
        self.rollout_state = rollout_sate
        self.rollout_state_reason = rollout_state_reason


class DeploymentCircuitBreaker(TypedDict):
    enable: bool
    rollback: bool


class LoadBalancer:
    def __init__(
        self,
        target_group_arn: Optional[str] = None,
        load_balancer_name: Optional[str] = None,
        container_name: Optional[str] = None,
        container_port: Optional[int] = None,
    ):
        self.target_group_arn = target_group_arn
        self.load_balancer_name = load_balancer_name
        self.container_name = container_name
        self.container_port = container_port


# https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service_definition_parameters.html#sd-deploymentconfiguration
class DeploymentConfiguration:
    def __init__(
        self,
        maximum_percent: int,
        minimum_healthy_percent: int,
        circuit_breaker: Optional[DeploymentCircuitBreaker] = None,
    ):
        self.maximum_percent = maximum_percent
        self.minimum_healthy_percent = minimum_healthy_percent
        self.circuit_breaker = circuit_breaker


class AwsVpcConfiguration:
    def __init__(
        self,
        subnets: List[str],
        security_groups: Optional[List[str]] = None,
        assign_public_ip: Optional[Literal["ENABLED", "DISABLED"]] = None,
    ):
        self.subnets = subnets
        self.security_groups = security_groups
        self.assign_public_ip = assign_public_ip


class NetworkConfiguration:
    def __init__(self, awsvpc_configuration: Optional[AwsVpcConfiguration] = None):
        self.awsvpc_configuration = awsvpc_configuration


class DeploymentController(TypedDict):
    type: Literal["ECS", "CODE_DEPLOY", "EXTERNAL"]


class PlacementStrategy(TypedDict):
    type: Optional[str]
    field: Optional[str]


class Service:
    DEFAULT_COLUMNS = [
        "name",
        "status",
        "desired",
        "running",
        "pending",
        "launch_type",
    ]

    def __init__(
        self,
        arn: str,
        name: str,
        cluster_arn: str,
        status: str,
        desired: int,
        running: int,
        pending: int,
        launch_type: Literal["EC2", "FARGATE"],
        task_definition: str,
        role_arn: str,
        created_at: datetime,
        created_by: str,
        scheduling_strategy: Literal["REPLICA", "DAEMON"],
        events: List[Event],
        enable_ecs_managed_tags: bool,
        enable_execute_command: bool,
        placement_constraints: List[PlacementConstraint],
        placement_strategy: List[PlacementStrategy],
        deployments: List[Deployment],
        load_balancers: List[LoadBalancer],
        propagate_tags: Optional[Literal["TASK_DEFINITION", "SERVICE", "NONE"]] = None,
        platform_version: Optional[str] = None,  # Only used for FARGATE tasks,
        deployment_configuration: Optional[DeploymentConfiguration] = None,
        deployment_controller: Optional[DeploymentController] = None,
        network_configuration: Optional[NetworkConfiguration] = None,
        tags: Optional[Dict[str, str]] = None,
    ):
        self.arn = arn
        self.name = name
        self.cluster_arn = cluster_arn
        self.status = status
        self.desired = desired
        self.running = running
        self.pending = pending
        self.launch_type = launch_type
        self.task_definition = task_definition
        self.role_arn = role_arn
        self.created_at = created_at
        self.created_by = created_by
        self.scheduling_strategy = scheduling_strategy
        self.events = events
        self.enable_ecs_managed_tags = enable_ecs_managed_tags
        self.enable_execute_command = enable_execute_command
        self.placement_constraints = placement_constraints
        self.placement_strategy = placement_strategy
        self.deployments = deployments
        self.load_balancers = load_balancers
        self.propagate_tags = propagate_tags
        self.platform_version = platform_version
        self.deployment_configuration = deployment_configuration
        self.deployment_controller = deployment_controller
        self.network_configuration = network_configuration
        self.tags = tags


class NetworkBinding:
    def __init__(
        self,
        bind_ip: str,
        container_port: int,
        host_port: int,
        protocol: Literal["tcp", "udp"],
    ):
        self.bind_ip = bind_ip
        self.container_port = container_port
        self.host_port = host_port
        self.protocol = protocol


class NetworkInterface:
    def __init__(self, attachment_id: str, ipv4_address: str, ipv6_address: str):
        self.attachment_id = attachment_id
        self.ipv4_address = ipv4_address
        self.ipv6_address = ipv6_address


class ManagedAgent:
    def __init__(self, name: str, reason: str, status: str, started_at: datetime):
        self.name = name
        self.reason = reason
        self.status = status
        self.started_at = started_at


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

    def __init__(
        self,
        arn: str,
        task_arn: str,
        name: str,
        image: str,
        image_digest: str,
        runtime_id: str,
        status: str,
        exit_code: int,
        reason: str,
        health: Literal["HEALTHY", "UNHEALTHY", "UNKNOWN"],
        cpu: int,
        memory: int,
        memory_reservation: int,
        network_bindings: List[NetworkBinding],
        network_interfaces: List[NetworkInterface],
        managed_agents: List[ManagedAgent],
        gpu_ids: List[str],
    ):
        self.id = arn.split("/")[-1]
        self.arn = arn
        self.task_id = task_arn.split("/")[-1]
        self.task_arn = task_arn
        self.name = name
        self.image = image
        self.image_digest = image_digest
        self.runtime_id = runtime_id
        self.status = status
        self.exit_code = exit_code
        self.reason = reason
        self.health = health
        self.cpu = cpu
        self.memory = memory
        self.memory_reservation = memory_reservation
        self.network_bindings = network_bindings
        self.network_interfaces = network_interfaces
        self.managed_agents = managed_agents
        self.gpu_ids = gpu_ids


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

    def __init__(
        self,
        arn: str,
        task_definition_arn: str,
        cluster_arn: str,
        container_instance_arn: str,
        availability_zone: str,
        connectivity: Literal["CONNECTED", "DISCONNECTED"],
        connectivity_at: datetime,
        created_at: datetime,
        status: Literal[
            "PROVISIONING",
            "ACTIVATING",
            "RUNNING",
            "DEPROVISIONING",
            "DEACTIVATING",
            "STOPPED",
        ],
        desired_status: str,
        health: Literal["HEALTHY", "UNHEALTHY", "UNKNOWN"],
        _type: Literal["EC2", "FARGATE", "EXTERNAL"],
        cpu: int,
        memory: int,
        group: str,
        pull_started_at: datetime,
        pull_stopped_at: datetime,
        started_at: datetime,
        started_by: str,
        stopped_at: Union[datetime, None],
        stopped_reason: str,
        tags: List[str],
        containers: List[Container],
    ):
        self.id = arn.split("/")[-1]
        self.arn = arn
        self.task_definition = task_definition_arn.split("/")[-1]
        self.task_definition_arn = task_definition_arn
        self.cluster_arn = cluster_arn
        self.availability_zone = availability_zone
        self.connectivity = connectivity
        self.connectivity_at = connectivity_at
        self.created_at = created_at
        self.status = status
        self.desired_status = desired_status
        self.health = health
        self.type = _type
        self.cpu = cpu
        self.memory = memory
        self.group = group
        self.pull_started_at = pull_started_at
        self.pull_stopped_at = pull_stopped_at
        self.started_at = started_at
        self.started_by = started_by
        self.stopped_at = stopped_at
        self.stopped_reason = stopped_reason
        self.tags = tags

        if self.type == "EC2":
            self.container_instance_id = container_instance_arn.split("/")[-1]
            self.container_instance_arn = container_instance_arn

        self.containers = containers

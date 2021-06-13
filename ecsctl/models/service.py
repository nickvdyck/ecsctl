from datetime import datetime
from ecsctl.models.common import PlacementConstraint
from typing import Dict, List, Literal, Optional, TypedDict


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

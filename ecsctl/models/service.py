from dataclasses import dataclass
from datetime import datetime
from ecsctl.models.common import PlacementConstraint
from typing import Dict, List, Literal, Optional, TypedDict


@dataclass(frozen=True)
class Event:
    DEFAULT_COLUMNS = [
        "id",
        "created_at",
        "message",
    ]

    id: str
    created_at: datetime
    message: str


@dataclass(frozen=True)
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

    id: str
    status: str
    task_definition: str
    desired: int
    pending: int
    running: int
    failed: int
    created_at: datetime
    updated_at: datetime
    launch_type: str
    rollout_state: str
    rollout_state_reason: str


class DeploymentCircuitBreaker(TypedDict):
    enable: bool
    rollback: bool


@dataclass(frozen=True)
class LoadBalancer:
    target_group_arn: Optional[str]
    load_balancer_name: Optional[str]
    container_name: Optional[str]
    container_port: Optional[int]


# https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service_definition_parameters.html#sd-deploymentconfiguration
@dataclass(frozen=True)
class DeploymentConfiguration:
    maximum_percent: int
    minimum_healthy_percent: int
    deployment_circuit_breaker: Optional[DeploymentCircuitBreaker]


@dataclass(frozen=True)
class AwsVpcConfiguration:
    subnets: List[str]
    security_groups: Optional[List[str]]
    assign_public_ip: Optional[Literal["ENABLED", "DISABLED"]]


@dataclass(frozen=True)
class NetworkConfiguration:
    awsvpc_configuration: Optional[AwsVpcConfiguration]


class DeploymentController(TypedDict):
    type: Literal["ECS", "CODE_DEPLOY", "EXTERNAL"]


class PlacementStrategy(TypedDict):
    type: Optional[str]
    field: Optional[str]


@dataclass(frozen=True)
class Service:
    DEFAULT_COLUMNS = [
        "name",
        "status",
        "desired",
        "running",
        "pending",
        "launch_type",
    ]

    arn: str
    name: str
    cluster_arn: str
    status: str
    desired: int
    running: int
    pending: int
    launch_type: Literal["EC2", "FARGATE"]
    task_definition: str
    role_arn: str
    created_at: datetime
    created_by: str
    scheduling_strategy: Literal["REPLICA", "DAEMON"]
    events: List[Event]
    enable_ecs_managed_tags: bool
    enable_execute_command: bool
    placement_constraints: List[PlacementConstraint]
    placement_strategy: List[PlacementStrategy]
    deployments: List[Deployment]
    load_balancers: List[LoadBalancer]
    propagate_tags: Optional[Literal["TASK_DEFINITION", "SERVICE", "NONE"]]
    platform_version: Optional[str]  # Only used for FARGATE tasks,
    deployment_configuration: Optional[DeploymentConfiguration]
    deployment_controller: Optional[DeploymentController]
    network_configuration: Optional[NetworkConfiguration]
    tags: Optional[Dict[str, str]]

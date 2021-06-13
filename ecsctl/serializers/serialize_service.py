from ecsctl.models import (
    AwsVpcConfiguration,
    Deployment,
    DeploymentConfiguration,
    Event,
    LoadBalancer,
    NetworkConfiguration,
    Service,
)
from typing import Any, Dict


def deserialize_deployment(deployment: Dict[str, Any]) -> Deployment:
    return Deployment(
        deployment["id"],
        deployment["status"],
        deployment["taskDefinition"],
        deployment["desiredCount"],
        deployment["pendingCount"],
        deployment["runningCount"],
        deployment["failedTasks"],
        deployment["createdAt"],
        deployment["updatedAt"],
        deployment["launchType"],
        deployment["rolloutState"],
        deployment["rolloutStateReason"],
    )


def serialize_deployment(deployment: Deployment) -> Dict[str, Any]:
    return {
        "id": deployment.id,
        "status": deployment.status,
        "task_definition": deployment.task_definition,
        "desired": deployment.desired,
        "pending": deployment.pending,
        "running": deployment.running,
        "failed": deployment.failed,
        "created_at": deployment.created_at.isoformat(),
        "updated_at": deployment.updated_at.isoformat(),
        "launch_type": deployment.launch_type,
        "rollout_state": deployment.rollout_state,
        "rollout_state_reason": deployment.rollout_state_reason,
    }


def deserialize_load_balancer(load_balancer: Dict[str, Any]) -> LoadBalancer:
    return LoadBalancer(
        load_balancer.get("targetGroupArn", None),
        load_balancer.get("loadBalancerName", None),
        load_balancer.get("containerName", None),
        load_balancer.get("containerPort", None),
    )


def serialize_load_balancer(load_balancer: LoadBalancer) -> Dict[str, Any]:
    json_dict = {
        "target_group_arn": load_balancer.target_group_arn,
        "load_balancer_name": load_balancer.load_balancer_name,
        "container_name": load_balancer.container_name,
        "container_port": load_balancer.container_port,
    }

    return {k: v for k, v in json_dict.items() if v is not None}


def deserialize_deployment_configuration(
    configuration: Dict[str, Any]
) -> DeploymentConfiguration:
    return DeploymentConfiguration(
        configuration["maximumPercent"],
        configuration["minimumHealthyPercent"],
        configuration.get("circuitBreaker", None),
    )


def serialize_deployment_configuration(
    configuration: DeploymentConfiguration,
) -> Dict[str, Any]:
    json_dict = {
        "maximum_percent": configuration.maximum_percent,
        "minimum_healthy_percent": configuration.minimum_healthy_percent,
        "circuit_breaker": configuration.circuit_breaker,
    }
    return {k: v for k, v in json_dict.items() if v is not None}


def deserialize_network_configuration(network: Dict[str, Any]) -> NetworkConfiguration:
    aws_vpc = network.get("awsvpcConfiguration", None)

    if aws_vpc is not None:
        aws_vpc_dict = aws_vpc
        aws_vpc = AwsVpcConfiguration(
            aws_vpc_dict["subnets"],
            aws_vpc_dict.get("securityGroups", None),
            aws_vpc_dict.get("assignPublicIP", None),
        )

    return NetworkConfiguration(aws_vpc)


def serialize_network_configuration(network: NetworkConfiguration) -> Dict[str, Any]:
    json_dict = {}

    if network.awsvpc_configuration is not None:
        awsvpc = network.awsvpc_configuration
        json_dict["awsvpc_configuration"] = {"subnets": awsvpc.subnets}

        if awsvpc.security_groups is not None:
            json_dict["security_groups"] = awsvpc.security_groups

        if awsvpc.assign_public_ip is not None:
            json_dict["assign_public_ip"] = awsvpc.assign_public_ip

    return {k: v for k, v in json_dict.items() if v is not None}


def deserialize_service(service: Dict[str, Any]) -> Service:
    deployment_configuration = service.get("deploymentConfiguration", None)

    if deployment_configuration is not None:
        deployment_configuration = deserialize_deployment_configuration(
            deployment_configuration
        )

    network_configuration = service.get("networkConfiguration", None)
    if network_configuration is not None:
        network_configuration = deserialize_network_configuration(network_configuration)

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
        [deserialize_service_event(event) for event in service.get("events", [])],
        service.get("enableECSManagedTags", False),
        service.get("enableExecuteCommand", False),
        service.get("placementConstraints", []),
        service.get("placementStrategy", []),
        [
            deserialize_deployment(deployment)
            for deployment in service.get("deployments", [])
        ],
        [deserialize_load_balancer(lb) for lb in service.get("loadBalancers", [])],
        service.get("propagateTags", None),
        service.get("platformVersion", None),
        deployment_configuration,
        service.get("deploymentController", None),
        network_configuration,
        service.get("tags", None),
    )


def serialize_service(service: Service) -> Dict[str, Any]:
    return {
        "arn": service.arn,
        "name": service.name,
        "cluster_arn": service.cluster_arn,
        "status": service.status,
        "desired": service.desired,
        "running": service.running,
        "pending": service.pending,
        "launch_type": service.launch_type,
        "task_definition": service.task_definition,
        "role_arn": service.role_arn,
        "created_at": service.created_at.isoformat(),
        "created_by": service.created_by,
        "scheduling_strategy": service.scheduling_strategy,
        "enable_ecs_managed_tags": service.enable_ecs_managed_tags,
        "enable_execute_command": service.enable_execute_command,
        "placement_constraints": service.placement_constraints,
        "placement_strategy": service.placement_strategy,
        "load_balancers": [
            serialize_load_balancer(lb) for lb in service.load_balancers
        ],
        "propagate_tags": service.propagate_tags,
        "platform_version": service.platform_version,
        "deployment_configuration": serialize_deployment_configuration(
            service.deployment_configuration
        )
        if service.deployment_configuration is not None
        else None,
        "network_configuration": serialize_network_configuration(
            service.network_configuration
        )
        if service.network_configuration is not None
        else None,
        "tags": service.tags,
    }


def deserialize_service_event(event: Dict[str, str]) -> Event:
    return Event(
        event["id"],
        event["createdAt"],
        event["message"],
    )


def serialize_service_event(event: Event) -> Dict[str, str]:
    return {
        "id": event.id,
        "created_at": event.created_at.isoformat(),
        "message": event.message,
    }

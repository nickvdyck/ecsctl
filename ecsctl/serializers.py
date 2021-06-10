from typing import Dict, Any
from ecsctl.models import (
    AwsVpcConfiguration,
    Cluster,
    Container,
    Deployment,
    DeploymentConfiguration,
    Instance,
    LoadBalancer,
    ManagedAgent,
    NetworkBinding,
    NetworkConfiguration,
    NetworkInterface,
    Service,
    Event,
    Task,
)


def serialize_ecs_cluster(cluster: Cluster) -> Dict[str, str]:
    return {
        "name": cluster.name,
        "status": cluster.status,
        "instances": cluster.status,
        "services": cluster.services,
        "running_tasks": cluster.running_tasks,
        "pending_tasks": cluster.pending_tasks,
    }


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
        [deserialize_ecs_service_event(event) for event in service.get("events", [])],
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


def serialize_ecs_service(service: Service) -> Dict[str, Any]:
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


def deserialize_ecs_service_event(event: Dict[str, str]) -> Event:
    return Event(
        event["id"],
        event["createdAt"],
        event["message"],
    )


def serialize_ecs_service_event(event: Event) -> Dict[str, str]:
    return {
        "id": event.id,
        "created_at": event.created_at,
        "message": event.message,
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
        "started_at": agent.started_at,
    }


def deserialize_container(container: Dict[str, Any]) -> Container:
    return Container(
        container["containerArn"],
        container["taskArn"],
        container["name"],
        container["image"],
        container.get("imageDigest", None),
        container["runtimeId"],
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


def deserialize_ecs_task(task: Dict[str, Any]) -> Task:
    return Task(
        task["taskArn"],
        task["taskDefinitionArn"],
        task["clusterArn"],
        task.get("containerInstanceArn", ""),
        task["availabilityZone"],
        task.get("connectivity", None),
        task.get("connectivityAt", None),
        task["createdAt"],
        task["lastStatus"],
        task["desiredStatus"],
        task["healthStatus"],
        task["launchType"],
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
    )


def serialize_ecs_task(task: Task) -> Dict[str, str]:
    task_json = {
        "id": task.id,
        "arn": task.arn,
        "task_definition": task.task_definition,
        "task_definition_arn": task.task_definition_arn,
        "cluster_arn": task.cluster_arn,
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

    if task.type == "ECS":
        task_json["container_instance_id"] = task.container_instance_id
        task_json["container_instance_arn"] = task.container_instance_arn

    if task.stopped_at is not None:
        task_json["stopped_at"] = task.stopped_at.isoformat()

    return task_json

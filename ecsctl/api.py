import boto3

from typing import List
from ecsctl.models import Cluster, Instance, Service, ServiceEvent, Task
from ecsctl.serializers import (
    deserialize_ec2_instance,
    deserialize_ecs_service,
    deserialize_ecs_task,
)
from ecsctl.utils import chunks


class EcsApi:
    def __init__(self, profile: str = None, region: str = None):
        session = boto3.session.Session(
            profile_name=profile,
            region_name=region,
        )

        self.client = session.client("ecs")

    def get_clusters(self, cluster_names: List[str]) -> List[Cluster]:
        cluster_arns = (
            cluster_names
            if len(cluster_names) > 0
            else self.client.list_clusters()["clusterArns"]
        )
        descriptors = self.client.describe_clusters(clusters=cluster_arns)

        clusters = [
            Cluster(
                cluster["clusterName"],
                cluster["status"],
                cluster["registeredContainerInstancesCount"],
                cluster["activeServicesCount"],
                cluster["runningTasksCount"],
                cluster["pendingTasksCount"],
            )
            for cluster in descriptors["clusters"]
        ]

        return clusters

    def get_instances(
        self, cluster_name: str, instance_names: List[str]
    ) -> List[Instance]:
        instance_arns = instance_names

        instances = []

        for instance_chunks in chunks(instance_arns, 100):
            descriptor = self.client.describe_container_instances(
                cluster=cluster_name, containerInstances=instance_chunks
            )

            instances = instances + [
                deserialize_ec2_instance(instance)
                for instance in descriptor["containerInstances"]
            ]

        return instances

    def get_services(self, cluster: str, service_names: List[str]) -> List[Service]:
        def list_all_service_arns(next_token=None):
            response = self.client.list_services(
                cluster=cluster, maxResults=100, nextToken=next_token or ""
            )

            service_arns = response["serviceArns"]
            next_token = response.get("nextToken", None)

            return (
                service_arns + list_all_service_arns(next_token)
                if next_token is not None
                else service_arns
            )

        service_arns = (
            list_all_service_arns() if len(service_names) == 0 else service_names
        )

        services = []

        for services_chunk in chunks(service_arns, 10):
            descriptor = self.client.describe_services(
                cluster=cluster, services=services_chunk
            )

            services = services + [
                deserialize_ecs_service(service) for service in descriptor["services"]
            ]

        return services

    def get_events_for_service(
        self, cluster: str, service_name: str
    ) -> List[ServiceEvent]:
        descriptor = self.client.describe_services(
            cluster=cluster, services=[service_name]
        )

        service = deserialize_ecs_service(descriptor["services"][0])
        return service.events

    def get_tasks_for_service(
        self, cluster: str, service_name: str, status: str = "RUNNING"
    ) -> List[Task]:
        def list_all_task_arns(next_token=None, desired_status: str = "RUNNING"):
            response = self.client.list_tasks(
                cluster=cluster,
                serviceName=service_name,
                maxResults=100,
                desiredStatus=desired_status,
                nextToken=next_token or "",
            )

            task_arns = response["taskArns"]
            next_token = response.get("nextToken", None)

            return (
                task_arns + list_all_task_arns(next_token)
                if next_token is not None
                else task_arns
            )

        task_arns = (
            list_all_task_arns(desired_status=status.upper())
            if status.upper() != "ALL"
            else list_all_task_arns(desired_status="RUNNING")
            + list_all_task_arns(desired_status="STOPPED")
        )

        tasks = []

        for tasks_chunk in chunks(task_arns, 100):
            descriptor = self.client.describe_tasks(
                cluster=cluster,
                tasks=tasks_chunk,
            )

            tasks = tasks + [deserialize_ecs_task(task) for task in descriptor["tasks"]]
        return tasks

    def get_task_by_id_or_arn(self, cluster: str, task_id_or_arn: str) -> Task:
        descriptor = self.client.describe_tasks(
            cluster=cluster,
            tasks=[task_id_or_arn],
        )

        return deserialize_ecs_task(descriptor["tasks"][0])

import boto3

from typing import Any, List, Literal, Optional
from ecsctl.models import Cluster, Instance, Service, Event, Task, TaskDefinition
from ecsctl.serializers import (
    deserialize_instance,
    deserialize_service,
    deserialize_ecs_task,
    deserialize_cluster,
    deserialize_task_definition,
)
from ecsctl.utils import chunks


class EcsService:
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
        clusters = [deserialize_cluster(cluster) for cluster in descriptors["clusters"]]

        return clusters

    def get_instances(
        self,
        cluster_name: str,
        instance_names: List[str],
        status: Optional[
            Literal[
                "ALL",
                "ACTIVE",
                "DRAINING",
                "REGISTERING",
                "DEREGISTERING",
                "REGISTRATION_FAILED",
                "INACTIVE",
            ]
        ] = None,
    ) -> List[Instance]:
        def list_all_instance_arns(
            next_token: Optional[str] = None, status: Optional[str] = None
        ):
            args = {
                "cluster": cluster_name,
                "maxResults": 100,
                "nextToken": next_token or "",
            }

            if status is not None:
                args["status"] = status

            response = self.client.list_container_instances(
                cluster=cluster_name,
                maxResults=100,
                nextToken=next_token or "",
            )

            instance_arns = response["containerInstanceArns"]
            next_token = response.get("nexttoken", None)
            return (
                instance_arns + list_all_instance_arns(next_token, status=status)
                if next_token is not None
                else instance_arns
            )

        if len(instance_names) == 0:
            instance_arns = [
                list_all_instance_arns(status=status)
                if (status or "").upper() != "ALL"
                else list_all_instance_arns()
                + list_all_instance_arns(status="INACTIVE")
            ]
        else:
            instance_arns = instance_names

        instance_arns = (
            list_all_instance_arns() if len(instance_names) == 0 else instance_names
        )

        instances = []

        for instance_chunks in chunks(instance_arns, 100):
            descriptor = self.client.describe_container_instances(
                cluster=cluster_name, containerInstances=instance_chunks
            )

            instances = instances + [
                deserialize_instance(instance)
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
                deserialize_service(service) for service in descriptor["services"]
            ]

        return services

    def get_events_for_service(self, cluster: str, service_name: str) -> List[Event]:
        descriptor = self.client.describe_services(
            cluster=cluster, services=[service_name]
        )
        services: List[Any] = descriptor["services"]
        service = None

        if len(services) > 0:
            service = deserialize_service(descriptor["services"][0])

        return service.events if service is not None else []

    def get_tasks(
        self,
        cluster: str,
        task_names_or_arns: Optional[List[str]] = None,
        instance: Optional[str] = None,
        service: Optional[str] = None,
        status: str = "RUNNING",
    ) -> List[Task]:
        def list_all_task_arns(next_token=None, desired_status: str = "RUNNING"):
            args = {
                "cluster": cluster,
                "maxResults": 100,
                "desiredStatus": desired_status,
                "nextToken": next_token or "",
            }

            if instance is not None:
                args["containerInstance"] = instance

            if service is not None:
                args["serviceName"] = service

            response = self.client.list_tasks(**args)

            task_arns = response["taskArns"]
            next_token = response.get("nextToken", None)

            return (
                task_arns + list_all_task_arns(next_token)
                if next_token is not None
                else task_arns
            )

        if len(task_names_or_arns or []) == 0:
            task_arns = (
                list_all_task_arns(desired_status=status.upper())
                if status.upper() != "ALL"
                else list_all_task_arns(desired_status="RUNNING")
                + list_all_task_arns(desired_status="STOPPED")
            )
        else:
            task_arns = task_names_or_arns

        tasks = []

        for tasks_chunk in chunks(task_arns, 100):
            descriptor = self.client.describe_tasks(
                cluster=cluster,
                tasks=tasks_chunk,
            )

            tasks = tasks + [deserialize_ecs_task(task) for task in descriptor["tasks"]]
        return tasks

    def get_containers(self, cluster: str, task_name):
        task = self.get_task_by_id_or_arn(cluster, task_id_or_arn=task_name)
        return task.containers

    def get_task_by_id_or_arn(self, cluster: str, task_id_or_arn: str) -> Task:
        descriptor = self.client.describe_tasks(
            cluster=cluster,
            tasks=[task_id_or_arn],
        )

        return deserialize_ecs_task(descriptor["tasks"][0])

    def get_task_definition(self, definition_family_rev_or_arn: str) -> TaskDefinition:
        descriptor = self.client.describe_task_definition(
            taskDefinition=definition_family_rev_or_arn
        )
        return deserialize_task_definition(descriptor["taskDefinition"])

import boto3
import click
import json
import os
import subprocess
import functools

from click import Context
from ecsctl.api import EcsApi
from ecsctl.config import Config
from ecsctl.serializers import (
    serialize_container,
    serialize_deployment,
    serialize_cluster,
    serialize_ecs_instance,
    serialize_ecs_service,
    serialize_ecs_service_event,
    serialize_ecs_task,
    serialize_task_definition,
)
from ecsctl.utils import ExceptionFormattedGroup, AliasedGroup
from ecsctl.console import Color, Console
from typing import Any, List, Tuple, TypedDict, Optional


class ContainerProps(TypedDict):
    profile: Optional[str]
    region: Optional[str]
    debug: bool


class ServiceProvider:
    def __init__(self, props: ContainerProps):
        self.props = props
        self.config = Config()
        self.console = Console()

    @functools.cached_property
    def ecs_api(
        self,
    ) -> EcsApi:
        return EcsApi(profile=self.props["profile"], region=self.props["region"])

    def resolve(self) -> Tuple[Config, Console]:
        return (self.config, self.console)

    def resolve_all(self) -> Tuple[Config, Console, EcsApi]:
        return (self.config, self.console, self.ecs_api)


def output_option(function: Any) -> Any:
    function = click.option("-o", "--output", envvar="ECS_CTL_OUTPUT", default="table")(
        function
    )
    return function


@click.group(cls=ExceptionFormattedGroup)
@click.option("-p", "--profile", envvar="AWS_PROFILE")
@click.option("-r", "--region", envvar="AWS_REGION")
@click.option("--debug", is_flag=True, default=False)
@click.pass_context
def cli(ctx: Context, profile: str, region: str, debug: bool):
    ctx.obj = ServiceProvider(
        props={
            "profile": profile,
            "region": region,
            "debug": debug,
        }
    )


@cli.group(short_help="ECSctl configuration")
def config():
    pass


@config.command(name="view")
@click.pass_obj
def config_view(obj: ServiceProvider):
    (config, console) = obj.resolve()
    console.print(json.dumps(config.to_json(), indent=4, sort_keys=True))


@config.command(name="set")
@click.argument("property", required=True)
@click.argument("value", required=True)
@click.pass_obj
def config_set(obj: ServiceProvider, property: str, value: str):
    (config, console) = obj.resolve()

    if property == "profile":
        config.set_profile(value)
        config.save()
    elif property == "default_cluster":
        config.set_default_cluster(value)
        config.save()
    else:
        console.print(f"Can't set property {property} to value {value}!", Color.RED)


@cli.group(short_help="Get ECS cluster resources", cls=AliasedGroup)
def get():
    pass


@get.command(name="clusters")
@click.argument("cluster_names", nargs=-1)
@output_option
@click.pass_obj
def get_clusters(obj: ServiceProvider, cluster_names: List[str], output: str):
    (_, console, ecs_api) = obj.resolve_all()

    clusters = ecs_api.get_clusters(cluster_names=list(cluster_names))

    clusters = sorted(clusters, key=lambda x: x.name)

    if output == "json":
        cluster_json = json.dumps([serialize_cluster(cluster) for cluster in clusters])
        console.print(cluster_json)
    else:
        console.table(clusters)


@get.command(name="instances")
@click.argument("instance_names", nargs=-1)
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.option("--status", default=None)
@click.option("--sort-by", required=False, default="registered_at")
@output_option
@click.pass_obj
def get_instances(
    obj: ServiceProvider,
    cluster: str,
    instance_names: Optional[List[str]],
    sort_by: Optional[str],
    status: Optional[str],  # TODO: make this a literal
    output: str,
):
    (config, console, ecs_api) = obj.resolve_all()

    instances = ecs_api.get_instances(
        cluster or config.default_cluster,
        instance_names=list(instance_names),
        status=status,
    )

    instances = sorted(instances, key=lambda x: x.__dict__[sort_by], reverse=True)

    if output == "json":
        console.print(
            json.dumps([serialize_ecs_instance(instance) for instance in instances])
        )
    else:
        console.table(instances)


@get.command(name="services")
@click.argument("service_names", nargs=-1)
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.option("--sort-by", required=False, default="name")
@output_option
@click.pass_obj
def get_services(
    obj: ServiceProvider,
    service_names: List[str],
    cluster: str,
    sort_by: str,
    output: str,
):
    (config, console, ecs_api) = obj.resolve_all()

    services = ecs_api.get_services(
        cluster or config.default_cluster, service_names=list(service_names)
    )

    services = sorted(services, key=lambda x: x.__dict__[sort_by], reverse=True)

    if output == "json":
        console.print(
            json.dumps([serialize_ecs_service(service) for service in services])
        )
    else:
        console.table(services)


@get.command(name="events")
@click.argument("service_name", nargs=1, required=True)
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@output_option
@click.pass_obj
def get_events(obj: ServiceProvider, service_name: str, cluster: str, output: str):
    (config, console, ecs_api) = obj.resolve_all()

    events = ecs_api.get_events_for_service(
        cluster or config.default_cluster, service_name=service_name
    )

    events = sorted(events, key=lambda x: x.created_at, reverse=True)

    if output == "json":
        console.print(
            json.dumps([serialize_ecs_service_event(event) for event in events])
        )
    else:
        if len(events) > 0:
            console.table(events)
        else:
            console.print(f"No events found for service '{service_name}'.")


@get.command(name="deployments")
@click.argument("service_name", nargs=1, required=True)
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@output_option
@click.pass_obj
def get_deployments(
    obj: ServiceProvider, service_name: str, cluster: str, output: str
) -> None:
    (_, console, ecs_api) = obj.resolve_all()

    services = ecs_api.get_services(cluster, service_names=[service_name])
    deployments = services[0].deployments

    deployments = sorted(deployments, key=lambda x: x.created_at, reverse=True)

    if output == "json":
        console.print(
            json.dumps([serialize_deployment(deployment) for deployment in deployments])
        )
    else:
        console.table(deployments)


@get.command(name="tasks")
@click.argument("task_names", nargs=-1, required=False)
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.option("-s", "--service", required=False)
@click.option("-i", "--instance", required=False)
@click.option("--status", default="RUNNING")
@output_option
@click.pass_obj
def get_tasks(
    obj: ServiceProvider,
    cluster: str,
    task_names: Optional[List[str]],
    instance: Optional[str],
    service: Optional[str],
    status: Optional[str],
    output: str,
):
    (config, console, ecs_api) = obj.resolve_all()

    tasks = ecs_api.get_tasks(
        cluster or config.default_cluster,
        task_names_or_arns=list(task_names),
        instance=instance,
        service=service,
        status=status,
    )

    if output == "json":
        console.print(json.dumps([serialize_ecs_task(task) for task in tasks]))
    else:
        if len(tasks) > 0:
            console.table(tasks)
        else:
            console.print("No tasks found for the given search criteria")


@get.command(name="containers")
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.argument("task_name")
@output_option
@click.pass_obj
def get_containers(obj: ServiceProvider, cluster: str, task_name: str, output: str):
    (config, console, ecs_api) = obj.resolve_all()

    containers = ecs_api.get_containers(cluster or config.default_cluster, task_name)
    if output == "json":
        console.print(
            json.dumps([serialize_container(container) for container in containers])
        )
    else:
        if len(containers) == 0:
            console.print("No containers found for the given search criteria.")
        else:
            console.table(containers)


@get.command(name="definitions")
@click.argument("definition_family_rev_or_arn")
@output_option
@click.pass_obj
def get_definitions(
    obj: ServiceProvider, definition_family_rev_or_arn: str, output: str
):
    (_, console, ecs_api) = obj.resolve_all()

    definition = ecs_api.get_task_definition(
        definition_family_rev_or_arn=definition_family_rev_or_arn
    )

    if output == "json":
        console.print(json.dumps(serialize_task_definition(definition)))
    else:
        console.table([definition])


@cli.command(short_help="Execute commands inside an ECS cluster")
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.option("-t", "--task", required=False)
@click.option("-s", "--service", required=False)
@click.option("--container", required=False)
@click.option("--command", required=False)
@click.option("--ec2", is_flag=True, default=False)
@click.pass_obj
def exec(
    obj: ServiceProvider,
    cluster: str,
    service: Optional[str],
    task: Optional[str],
    container: Optional[str],
    command: Optional[str],
    ec2: bool,
):
    profile = obj.props.get("profile")
    region = obj.props.get("region")
    (config, console, ecs_api) = obj.resolve_all()

    if not config.meets_ssm_prereqs:
        console.print(
            "This feature requires the following to be setup correctly:",
            color=Color.YELLOW,
        )
        console.print(
            "     - You have the AWS cli installed and available on your PATH.",
            color=Color.YELLOW,
        )
        console.print(
            "     - You have SSM setup and working correctly.", color=Color.YELLOW
        )
        console.print(
            "     - You have the SSM AWS cli plugin installed: https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html",
            color=Color.YELLOW,
        )
        console.print("")

        response = console.input(
            "Do you have all prerequisites setup correctly? (y/N) "
        )

        if response.lower() == "y":
            config.set_meets_ssm_prereqs()
            config.save()
        else:
            return

    selected_cluster = cluster or config.default_cluster

    if task is None and service is None:
        raise Exception("Error: service or task must be specified")

    if task is None and service is not None:
        tasks = ecs_api.get_tasks(cluster=selected_cluster, service=service)
        _, index = console.choose("Choose a task:", [task.arn for task in tasks])
        selected_task = tasks[index]

    else:
        selected_task = ecs_api.get_task_by_id_or_arn(
            cluster or config.default_cluster, task
        )

    if ec2:
        constainer_instances = ecs_api.get_instances(
            cluster or config.default_cluster, [selected_task.container_instance_id]
        )

        ec2_instance = constainer_instances[0].ec2_instance

        cmd = ["aws"]

        if profile is not None:
            cmd = cmd + ["--profile", profile]

        if region is not None:
            cmd = cmd + ["--region", region]

        cmd = cmd + [
            "ssm",
            "start-session",
            "--target",
            ec2_instance,
        ]
    else:
        if container is None:
            _, index = console.choose(
                "Choose a container:",
                [container.name for container in selected_task.containers],
            )
            selected_container = selected_task.containers[index].name
        else:
            selected_container = container

        cmd = ["aws"]

        if profile is not None:
            cmd = cmd + ["--profile", profile]

        if region is not None:
            cmd = cmd + ["--region", region]

        cmd = cmd + [
            "ecs",
            "execute-command",
            "--cluster",
            selected_cluster,
            "--task",
            selected_task.arn,
            "--container",
            selected_container,
            "--interactive",
            "--command",
            command or "/bin/sh",
        ]

    env = os.environ.copy()

    shell = subprocess.Popen(cmd, env=env)

    while True:
        try:
            shell.wait()
            break
        except KeyboardInterrupt as _:
            pass


@cli.command(short_help="Execute commands inside an ECS cluster")
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.option("-t", "--task", "task_name", required=False)
@click.option("--container", "container_name", required=False)
@click.pass_obj
def logs(
    obj: ServiceProvider,
    cluster: str,
    task_name: Optional[str],
    container_name: Optional[str],
):
    (_, _, ecs_api) = obj.resolve_all()
    task = ecs_api.get_task_by_id_or_arn(
        cluster=cluster or obj.config.default_cluster, task_id_or_arn=task_name
    )

    definition = ecs_api.get_task_definition(
        definition_family_rev_or_arn=task.task_definition_arn
    )

    client = boto3.client("logs")
    paginator = client.get_paginator("filter_log_events")

    # paginator.

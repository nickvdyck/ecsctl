import click
import json
import os
import subprocess

from click import Context
from ecsctl import console
from ecsctl.api import EcsApi
from ecsctl.config import Config
from ecsctl.serializers import (
    serialize_container,
    serialize_ecs_cluster,
    serialize_ecs_instance,
    serialize_ecs_service,
    serialize_ecs_service_event,
    serialize_ecs_task,
)
from ecsctl.utils import ExceptionFormattedGroup, AliasedGroup
from ecsctl.console import Color, Console
from typing import List, Tuple, Dict, Optional


class Dependencies:
    def __init__(
        self, config: Config, ecs_api: EcsApi, props: Dict[str, str], console: Console
    ):
        self.config = config
        self.ecs_api = ecs_api
        self.props = props
        self.console = console


def get_dependencies(
    dep: Dependencies,
) -> Tuple[Config, EcsApi, Dict[str, str], Console]:
    return (dep.config, dep.ecs_api, dep.props, dep.console)


@click.group(cls=ExceptionFormattedGroup)
@click.option("-p", "--profile", envvar="AWS_PROFILE")
@click.option("-r", "--region", envvar="AWS_REGION")
@click.option("-o", "--output", envvar="ECS_CTL_OUTPUT", default="table")
@click.pass_context
def cli(ctx: Context, profile: str, region: str, output: str):
    config = Config()
    console = Console()
    ctx.obj = Dependencies(
        config,
        None,
        {"profile": profile, "output": output, "region": region},
        console,
    )


@cli.group(short_help="ECSctl configuration")
def config():
    pass


@config.command(name="view")
@click.pass_obj
def config_view(obj: Dependencies):
    config = obj.config
    console = obj.console
    console.print(json.dumps(config.to_json(), indent=4, sort_keys=True))


@config.command(name="set")
@click.pass_obj
@click.argument("property", required=True)
@click.argument("value", required=True)
def config_set(obj: Dependencies, property: str, value: str):
    config = obj.config
    console = obj.console

    if property == "profile":
        config.set_profile(value)
        config.save()
    elif property == "default_cluster":
        config.set_default_cluster(value)
        config.save()
    else:
        console.print(f"Can't set property {property} to value {value}!", Color.RED)


@cli.group(short_help="Get ECS cluster resources", cls=AliasedGroup)
@click.pass_obj
def get(obj: Dependencies):
    config = obj.config
    profile = obj.props.get("profile")
    region = obj.props.get("region")
    # TODO: bail out when profile is None
    ecs_api = EcsApi(profile or config.profile, region)
    obj.ecs_api = ecs_api


@get.command(name="clusters")
@click.argument("cluster_names", nargs=-1)
@click.pass_context
def get_clusters(ctx: Context, cluster_names: List[str]):
    (_, ecs_api, props, console) = get_dependencies(ctx.obj)

    clusters = ecs_api.get_clusters(cluster_names=list(cluster_names))

    clusters = sorted(clusters, key=lambda x: x.name)

    if props.get("output", None) == "json":
        cluster_json = json.dumps(
            [serialize_ecs_cluster(cluster) for cluster in clusters]
        )
        console.print(cluster_json)
    else:
        console.table(clusters)


@get.command(name="instances")
@click.argument("instance_names", nargs=-1)
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.option("--status", default=None)
@click.option("--sort-by", required=False, default="registered_at")
@click.pass_context
def get_instances(
    ctx: Context,
    cluster: str,
    instance_names: Optional[List[str]],
    sort_by: Optional[str],
    status: Optional[str],  # TODO: make this a literal
):
    (config, ecs_api, props, console) = get_dependencies(ctx.obj)

    instances = ecs_api.get_instances(
        cluster or config.default_cluster,
        instance_names=list(instance_names),
        status=status,
    )

    instances = sorted(instances, key=lambda x: x.__dict__[sort_by], reverse=True)

    if props.get("output", None) == "json":
        console.print(
            json.dumps([serialize_ecs_instance(instance) for instance in instances])
        )
    else:
        console.table(instances)


@get.command(name="services")
@click.argument("service_names", nargs=-1)
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.option("--sort-by", required=False, default="name")
@click.pass_context
def get_services(ctx: Context, service_names: List[str], cluster: str, sort_by: str):
    (config, ecs_api, props, console) = get_dependencies(ctx.obj)

    services = ecs_api.get_services(
        cluster or config.default_cluster, service_names=list(service_names)
    )

    services = sorted(services, key=lambda x: x.__dict__[sort_by], reverse=True)

    if props.get("output", None) == "json":
        console.print(
            json.dumps([serialize_ecs_service(service) for service in services])
        )
    else:
        console.table(services)


@get.command(name="events")
@click.argument("service_name", nargs=1, required=True)
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.pass_context
def get_events(ctx: Context, service_name: str, cluster: str):
    (config, ecs_api, props, console) = get_dependencies(ctx.obj)

    events = ecs_api.get_events_for_service(
        cluster or config.default_cluster, service_name=service_name
    )

    events = sorted(events, key=lambda x: x.created_at, reverse=True)

    if props.get("output", None) == "json":
        console.print(
            json.dumps([serialize_ecs_service_event(event) for event in events])
        )
    else:
        console.table(events)


@get.command(name="tasks")
@click.argument("task_names", nargs=-1, required=False)
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.option("-s", "--service", required=False)
@click.option("-i", "--instance", required=False)
@click.option("--status", default="RUNNING")
@click.pass_context
def get_tasks(
    ctx: Context,
    cluster: str,
    task_names: Optional[List[str]],
    instance: Optional[str],
    service: Optional[str],
    status: Optional[str],
):
    (config, ecs_api, props, console) = get_dependencies(ctx.obj)

    tasks = ecs_api.get_tasks(
        cluster or config.default_cluster,
        task_names_or_arns=list(task_names),
        instance=instance,
        service=service,
        status=status,
    )

    if props.get("output", None) == "json":
        console.print(json.dumps([serialize_ecs_task(task) for task in tasks]))
    else:
        if len(tasks) > 0:
            console.table(tasks)
        else:
            console.print("No tasks found for the given search criteria")


@get.command(name="containers")
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.argument("task_name")
@click.pass_context
def get_containers(ctx: Context, cluster: str, task_name: str):
    (config, ecs_api, props, console) = get_dependencies(ctx.obj)

    containers = ecs_api.get_containers(cluster or config.default_cluster, task_name)
    if props.get("output", None) == "json":
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
@click.pass_context
def get_containers(ctx: Context, definition_family_rev_or_arn: str):
    (_, ecs_api, _, console) = get_dependencies(ctx.obj)

    definition = ecs_api.get_task_definition(
        definition_family_rev_or_arn=definition_family_rev_or_arn
    )

    definition["registeredAt"] = definition["registeredAt"].isoformat()

    if definition.get("deregisteredAt", None) is not None:
        definition["deregisteredAt"] = definition["deregisteredAt"].isoformat()

    console.print(json.dumps(definition))


@cli.command(short_help="Execute commands inside an ECS cluster")
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.option("-t", "--task", required=False)
@click.option("-s", "--service", required=False)
@click.option("--ec2", is_flag=True, default=False)
@click.pass_context
def exec(ctx: Context, cluster: str, task: str, service: str, ec2: bool):
    if not ec2:
        raise Exception(
            "Only executing into an ec2 instance supported at the moment. Please add --ec2 to jump into a shell in the ec2 instance a service or task is running on."
        )

    (config, ecs_api, props, console) = get_dependencies(ctx.obj)

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

    task = ecs_api.get_task_by_id_or_arn(cluster or config.default_cluster, task)

    constainer_instances = ecs_api.get_instances(
        cluster or config.default_cluster, [task.container_instance_id]
    )

    ec2_instance = constainer_instances[0].ec2_instance

    if props.get("profile", None) is None:
        cmd = ["aws", "ssm", "start-session", "--target", ec2_instance]
    else:
        cmd = [
            "aws",
            "--profile",
            props.get("profile"),
            "ssm",
            "start-session",
            "--target",
            ec2_instance,
        ]

    env = os.environ.copy()

    shell = subprocess.Popen(cmd, env=env)

    while True:
        try:
            shell.wait()
            break
        except KeyboardInterrupt as _:
            pass

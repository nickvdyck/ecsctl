import click
import json
import math
import os
import subprocess

from click import Context
from ecsctl import __version__
from ecsctl.utils import AliasedGroup, BASE_SHELL_COLORS, ExceptionFormattedGroup
from ecsctl.services.provider import ServiceProvider
from ecsctl.services.console import Color
from ecsctl.serializers import (
    serialize_container,
    serialize_deployment,
    serialize_cluster,
    serialize_instance,
    serialize_service,
    serialize_service_event,
    serialize_task,
    serialize_task_definition,
)
from typing import Any, List, Optional


def output_option(function: Any) -> Any:
    function = click.option("-o", "--output", envvar="ECS_CTL_OUTPUT", default="table")(
        function
    )
    return function


@click.group(cls=ExceptionFormattedGroup)
@click.version_option(version=__version__)
@click.option("-p", "--profile", envvar="AWS_PROFILE")
@click.option("-r", "--region", envvar="AWS_REGION")
@click.option(
    "--debug", help="Print verbose error messages", is_flag=True, default=False
)
@click.pass_context
def cli(ctx: Context, profile: str, region: str, debug: bool):
    ctx.obj = ServiceProvider(
        props={
            "profile": profile,
            "region": region,
            "debug": debug,
        }
    )


@cli.group(short_help="Modify ecsctl config files")
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
            json.dumps([serialize_instance(instance) for instance in instances])
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
        console.print(json.dumps([serialize_service(service) for service in services]))
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
        console.print(json.dumps([serialize_service_event(event) for event in events]))
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
    (config, console, ecs_api) = obj.resolve_all()

    services = ecs_api.get_services(
        cluster or config.default_cluster, service_names=[service_name]
    )
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
        console.print(json.dumps([serialize_task(task) for task in tasks]))
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


@cli.command(short_help="Execute commands inside a container or EC2 instance.")
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
        if selected_task.container_instance_id is None:
            raise Exception(
                f"Task not running on an EC2 backed instance, launch type is {selected_task.launch_type}."
            )

        constainer_instances = ecs_api.get_instances(
            cluster or config.default_cluster, [selected_task.container_instance_id]
        )

        ec2_instance = constainer_instances[0].ec2_instance_id

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
        except KeyboardInterrupt:
            pass


@cli.command(short_help="Print the logs from a container in a service or task")
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.option("-s", "--service", "service_name", required=False)
@click.option("-t", "--task", "task_name", required=False)
@click.option("--container", "container_name", required=False)
@click.option("--start", required=False)
@click.option("--tail", is_flag=True, default=False)
@click.pass_obj
def logs(
    obj: ServiceProvider,
    cluster: str,
    service_name: Optional[str],
    task_name: Optional[str],
    container_name: Optional[str],
    start: Optional[str],
    tail: bool,
):
    if service_name is None and task_name is None:
        raise Exception("Invalid options: either --service or --task is required.")

    (config, console, ecs_api) = obj.resolve_all()
    aws_logs = obj.logs

    cluster = cluster or config.default_cluster

    if service_name is not None:
        tasks = ecs_api.get_tasks(cluster=cluster, service=service_name)
    else:
        tasks = ecs_api.get_tasks(cluster=cluster, task_names_or_arns=[task_name])

    if len(tasks) == 0:
        raise Exception("No tasks found for given options!")

    # TODO: Multiple task definitions can have different configurations!
    task = tasks[0]
    definition = ecs_api.get_task_definition(
        definition_family_rev_or_arn=task.task_definition_arn
    )

    if container_name is None:
        (container_name, _) = console.choose(
            "Pick a container:",
            [container.name for container in definition.container_definitions],
        )

    container_definition = next(
        (x for x in definition.container_definitions if x.name == container_name), None
    )

    if container_definition is None:
        raise Exception(f"Can't find definition for container {container_name}.")

    log_configuration = container_definition.log_configuration
    if log_configuration is None or log_configuration.log_driver != "awslogs":
        raise Exception(
            f"Invalid logconfiguration for {container_name}, only awslogs supported!"
        )

    group = log_configuration.options["awslogs-group"]
    prefix = log_configuration.options["awslogs-stream-prefix"]

    stream_names = [f"{prefix}/{container_name}/{task.id}" for task in tasks]

    log_generator = aws_logs.query_logs(
        group_name=group,
        stream_names=stream_names,
        start_time=start,
        end_time=None,
        tail=tail,
    )

    multiple = math.ceil(len(stream_names) / len(BASE_SHELL_COLORS))
    color_map = dict(zip(stream_names, BASE_SHELL_COLORS * multiple))

    task_num = len(tasks)
    for log_line in log_generator:
        if task_num > 1:
            task_id = log_line.log_stream_name.split("/")[-1]
            color = color_map.get(log_line.log_stream_name, "green")
            click.echo(click.style(task_id, fg=color), nl=False)
            click.echo(": ", nl=False)
            click.echo(log_line.message)
        else:
            console.print(log_line.message)


@cli.group(short_help="Manage and rollout ECS deployments", cls=AliasedGroup)
def rollout():
    pass


@rollout.command(name="restart")
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.argument("service_name")
@click.pass_obj
def rollout_restart(obj: ServiceProvider, cluster: str, service_name: str):
    (config, console, ecs_api) = obj.resolve_all()

    cluster = cluster or config.default_cluster

    redeployed_service = ecs_api.redeploy_service(cluster=cluster, service=service_name)

    console.print(f"Redeployed {redeployed_service.name}: {redeployed_service.status}!")

import click
import json
import os
import subprocess

from click import Context
from ecsctl.api import EcsApi
from ecsctl.config import Config
from ecsctl.utils import render_table
from ecsctl.serializers import (
    serialize_ecs_cluster,
    serialize_ecs_service,
    serialize_ecs_task,
)
from rich import print
from typing import List, Tuple, Dict


class Dependencies:
    def __init__(self, config: Config, ecs_api: EcsApi, props: Dict[str, str]):
        self.config = config
        self.ecs_api = ecs_api
        self.props = props


def get_dependencies(dep: Dependencies) -> Tuple[Config, EcsApi, Dict[str, str]]:
    return (dep.config, dep.ecs_api, dep.props)


@click.group()
@click.option("--profile", envvar="AWS_PROFILE")
@click.option("--region", envvar="AWS_REGION")
@click.option("--output", envvar="ECS_CTL_OUTPUT", default="table")
@click.pass_context
def cli(ctx: Context, profile: str, region: str, output: str):
    config = Config()
    # TODO: bail out when profile is None
    ecs_api = EcsApi(profile or config.profile)

    ctx.obj = Dependencies(
        config, ecs_api, {"profile": profile, "output": output, "region": region}
    )


@cli.group(short_help="Get ECS cluster resources")
def get():
    pass


@get.command(name="clusters")
@click.argument("cluster_names", nargs=-1)
@click.pass_context
def get_clusters(ctx: Context, cluster_names: List[str]):
    (_, ecs_api, props) = get_dependencies(ctx.obj)

    clusters = ecs_api.get_clusters(cluster_names=list(cluster_names))

    clusters = sorted(clusters, key=lambda x: x.name)

    if props.get("output", None) == "json":
        cluster_json = json.dumps(
            [serialize_ecs_cluster(cluster) for cluster in clusters]
        )
        print(cluster_json)
    elif props.get("output", None) == "pretty":
        print([serialize_ecs_cluster(cluster) for cluster in clusters])
    else:
        render_table(clusters)


@get.command(name="instances")
@click.argument("instance_names", nargs=-1)
@click.option("--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.pass_context
def get_instances(ctx: Context, instance_names: List[str], cluster: str):
    (config, ecs_api, _) = get_dependencies(ctx.obj)

    instances = ecs_api.get_instances(
        cluster or config.default_cluster, instance_names=list(instance_names)
    )

    render_table(instances)


@get.command(name="services")
@click.argument("service_names", nargs=-1)
@click.option("--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.pass_context
def get_services(ctx: Context, service_names: List[str], cluster: str):
    (config, ecs_api, props) = get_dependencies(ctx.obj)

    services = ecs_api.get_services(
        cluster or config.default_cluster, service_names=list(service_names)
    )

    services = sorted(services, key=lambda x: x.name)

    if props.get("output", None) == "json":
        print(json.dumps([serialize_ecs_service(service) for service in services]))
    elif props.get("output", None) == "pretty":
        print([serialize_ecs_service(service) for service in services])
    else:
        render_table(services)


@get.command(name="events")
@click.argument("service_name", nargs=1, required=True)
@click.option("--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.pass_context
def get_events(ctx: Context, service_name: str, cluster: str):
    (config, ecs_api, _) = get_dependencies(ctx.obj)

    events = ecs_api.get_events_for_service(
        cluster or config.default_cluster, service_name=service_name
    )

    events = sorted(events, key=lambda x: x.created_at, reverse=True)
    render_table(events)

    # if props.get("output", None) == "json":
    #     print(json.dumps([serialize_ecs_service(service) for service in services]))
    # if props.get("output", None) == "pretty":
    #     print([serialize_ecs_service(service) for service in services])
    # else:
    #     render_table(services)


@get.command(name="tasks")
@click.argument("service_name", nargs=1, required=True)
@click.option("--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.option("--status", default="RUNNING")
@click.pass_context
def get_tasks(ctx: Context, service_name: str, cluster: str, status: str):
    (config, ecs_api, props) = get_dependencies(ctx.obj)

    tasks = ecs_api.get_tasks_for_service(
        cluster or config.default_cluster,
        service_name=service_name,
        status=status,
    )

    if props.get("output", None) == "json":
        print(json.dumps([serialize_ecs_task(task) for task in tasks]))
    elif props.get("output", None) == "pretty":
        print([serialize_ecs_task(task) for task in tasks])
    else:
        render_table(tasks)


@cli.command(short_help="Execute commands inside an ECS cluster")
@click.option("--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.option("--task", required=False)
@click.pass_context
def exec(ctx: Context, cluster: str, task: str):
    (config, ecs_api, props) = get_dependencies(ctx.obj)
    task = ecs_api.get_task_by_id_or_arn(cluster or config.default_cluster, task)

    constainer_instances = ecs_api.get_instances(
        cluster or config.default_cluster, [task.container_instance_id]
    )

    render_table(constainer_instances)
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
    # env['AWS_PROFILE'] = profile
    # env['AWS_DEFAULT_REGION'] = region

    p = subprocess.Popen(cmd, env=env)

    while True:
        try:
            p.wait()
            break
        except KeyboardInterrupt as e:
            pass

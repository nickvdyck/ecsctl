import functools

from boto3.session import Session
from ecsctl.services.ecs import EcsService
from ecsctl.services.logs import AWSLogs
from ecsctl.services.console import Console, Color
from ecsctl.services.config import Config

from typing import Optional, Tuple, TypedDict


class Props(TypedDict):
    profile: Optional[str]
    region: Optional[str]
    debug: bool


class ServiceProvider:
    def __init__(self, props: Props):
        self.props = props
        self.config = Config()
        self.console = Console()

    @functools.cached_property
    def session(
        self,
    ) -> Session:
        return Session(
            profile_name=self.props.get("profile", None),
            region_name=self.props.get("region", None),
        )

    @functools.cached_property
    def ecs_api(
        self,
    ) -> EcsService:
        return EcsService(profile=self.props["profile"], region=self.props["region"])

    @functools.cached_property
    def logs(
        self,
    ) -> AWSLogs:
        return AWSLogs(self.session)

    def resolve(self) -> Tuple[Config, Console]:
        return (self.config, self.console)

    def resolve_all(self) -> Tuple[Config, Console, EcsService]:
        return (self.config, self.console, self.ecs_api)

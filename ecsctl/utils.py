import click
import typing

from click.core import Context
from ecsctl.config import Config
from typing import List, Any


# stolen from: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(items: List[Any], n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(items), n):
        yield items[i : i + n]


class ExceptionFormattedGroup(click.Group):
    def resolve_command(self, ctx: Context, args: List[str]):
        self.__called_with_params = ctx.params
        return super().resolve_command(ctx, args)

    def __call__(self, *args, **kwargs):
        try:
            return self.main(*args, **kwargs)
        except Exception as ex:
            if "--debug" in self.__called_with_params:
                click.echo(ex)
            else:
                message = click.style(ex, fg="red")
                click.echo(message=message, err=True)


class AliasedGroup(click.Group):
    def get_command(self, ctx: Context, cmd_name: str):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv

        if ctx.obj.config is None:
            return None

        config = typing.cast(Config, ctx.obj.config)
        resolved = config.resolve_alias(cmd_name)

        if resolved is None:
            return None

        matches = [x for x in self.list_commands(ctx) if x == resolved]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")

    def resolve_command(self, ctx: Context, args: List[str]):
        # always return the full command name
        _, cmd, args = super().resolve_command(ctx, args)
        return cmd.name, cmd, args

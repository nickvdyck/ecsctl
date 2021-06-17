import functools
import os
import sys
import stat

from datetime import datetime
from enum import Enum
from tabulate import tabulate
from typing import Any, List, Optional, Tuple
from simple_term_menu import TerminalMenu


def render_column(item: Any) -> str:
    if isinstance(item, datetime):
        return item.strftime("%Y/%m/%d %H:%M:%S")
    elif item is None:
        return ""
    else:
        return str(item)


class Color(Enum):
    RED = "\u001b[31m"
    YELLOW = "\u001b[33m"
    _RESET = "\u001b[0m"


class Console:
    def input(self, message: str) -> str:
        return input(message)

    def print(self, message: Any, color: Optional[Color] = None):
        reset: Optional[Color] = None
        if color is not None:
            reset = Color._RESET

        print(f"{color or ''}{message}{reset or ''}", flush=self.is_output_redirected())

    def table(self, items: List[Any]):
        first = items[0]

        table_headers = [
            head.upper().replace("_", " ") for head in first.__class__.DEFAULT_COLUMNS
        ]
        table_body = [
            [
                render_column(row.__dict__[name])
                for name in row.__class__.DEFAULT_COLUMNS
            ]
            for row in items
        ]

        print(
            tabulate(
                table_body,
                headers=table_headers,
                tablefmt="plain",
                numalign="left",
                stralign="left",
            )
        )

    @functools.lru_cache(maxsize=1)
    def is_output_redirected(self) -> bool:
        if os.isatty(sys.stdout.fileno()):
            return False
        else:
            mode = os.fstat(1).st_mode
            if stat.S_ISFIFO(mode):
                return True
            elif stat.S_ISREG(mode):
                return True
            else:
                return False

    def choose(self, title: str, options: List[str]) -> Tuple[str, int]:
        if self.is_output_redirected():
            raise Exception("Can't render selection when output is redirected!")

        terminal_menu = TerminalMenu(options, title=title)
        index = terminal_menu.show()
        return (options[index], index)

from datetime import datetime
from typing import List, Any

from rich import print
from rich import box
from rich.table import Table


# stolen from: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def render_table(items: List[Any]):
    first_item = items[0]
    table = Table(
        *[col.upper().replace("_", " ") for col in first_item.__class__.DEFAULT_COLUMNS],
        box=box.SIMPLE,
    )

    for item in items:
        row = [
            render_column(item.__dict__[name])
            for name in item.__class__.DEFAULT_COLUMNS
        ]
        table.add_row(*row)

    print(table)


def render_column(item: Any) -> str:
    if isinstance(item, datetime):
        return item.strftime("%Y/%m/%d %H:%M:%S")
    elif item is None:
        return ""
    else:
        return str(item)

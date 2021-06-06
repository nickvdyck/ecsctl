from typing import List, Any

# stolen from: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(items: List[Any], n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(items), n):
        yield items[i : i + n]

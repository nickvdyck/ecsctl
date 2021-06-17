from ecsctl.models.log import LogLine
from typing import Any, Dict


def deserialize_log_line(line: Dict[str, Any]) -> LogLine:
    return LogLine(
        line["logStreamName"],
        line["timestamp"],
        line["message"],
        line["ingestionTime"],
        line["eventId"],
    )

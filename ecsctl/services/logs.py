from ecsctl.serializers.serialize_log import deserialize_log_line
import re
import time

from boto3.session import Session
from ecsctl.models.log import LogLine
from collections import deque
from datetime import datetime, timedelta
from dateutil.parser import parse
from dateutil.tz import tzutc
from typing import Generator, Optional, Union


ONE_MINUTE = 60
ONE_HOUR = 60 * ONE_MINUTE
ONE_DAY = 24 * ONE_HOUR
ONE_WEEK = 7 * ONE_DAY

TIMINGS = {"m": ONE_MINUTE, "h": ONE_HOUR, "d": ONE_DAY, "w": ONE_WEEK}


class AWSLogs:
    DEFAULT_TAIL_INTERVAL = 5
    MAX_EVENTS_PER_CALL = 10000
    TIME_AGO_REGEX = (
        r"(\d+)\s?(m|minute|minutes|h|hour|hours|d|day|days|w|weeks|weeks)(?: ago)?"
    )

    def __init__(self, session: Session):
        self.session = session
        self.client = session.client("logs")
        self.tail_interval = self.DEFAULT_TAIL_INTERVAL

    def query_logs(
        self,
        group_name: str,
        stream_name: str,
        start_time: Optional[str],
        end_time: Optional[str],
        tail: bool = False,
    ) -> Generator[LogLine, None, None]:
        start_timestamp = self.parse_time_ago(start_time)
        end_timestamp = self.parse_time_ago(end_time)

        do_wait = object()

        def log_generator() -> Generator[Union[LogLine, object], None, None]:
            interleaving_sanity = deque(maxlen=self.MAX_EVENTS_PER_CALL)
            kwargs = {
                "logGroupName": group_name,
                "logStreamNames": [stream_name],
                "interleaved": True,
            }

            if start_timestamp is not None:
                kwargs["startTime"] = start_timestamp

            if end_timestamp is not None:
                kwargs["endTime"] = end_timestamp

            while True:
                response = self.client.filter_log_events(**kwargs)

                for event in response.get("events", []):
                    log_line = deserialize_log_line(event)

                    if log_line.event_id not in interleaving_sanity:
                        interleaving_sanity.append(log_line.event_id)
                        yield log_line

                if "nextToken" in response:
                    kwargs["nextToken"] = response["nextToken"]
                else:
                    yield do_wait

        for log_line in log_generator():
            if log_line is do_wait:
                if tail:
                    time.sleep(self.tail_interval)
                    continue
                else:
                    return

            yield log_line

    def parse_time_ago(self, timing: Optional[str]) -> Optional[int]:
        if timing is None:
            return None

        ago_match = re.match(self.TIME_AGO_REGEX, timing)

        if ago_match:
            amount, unit = ago_match.groups()
            amount = int(amount)
            unit_as_seconds = TIMINGS[unit[0]]
            date = datetime.utcnow() + timedelta(
                seconds=float(unit_as_seconds * amount * -1)
            )
        else:
            try:
                date = parse(timing)
            except ValueError:
                raise Exception(f"Unknown date: {timing}")

        if date.tzinfo:
            if date.utcoffset != 0:
                date = date.astimezone(tzutc())
            date = date.replace(tzinfo=None)

        return int((date - datetime(1970, 1, 1)).total_seconds()) * 1000

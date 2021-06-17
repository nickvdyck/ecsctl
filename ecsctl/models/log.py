from dataclasses import dataclass


@dataclass(frozen=True)
class LogLine:
    __slots__ = (
        "log_stream_name",
        "timestamp",
        "message",
        "ingestion_time",
        "event_id",
    )
    log_stream_name: str
    timestamp: int
    message: str
    ingestion_time: int
    event_id: str

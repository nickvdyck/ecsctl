from ecsctl.models.log import LogLine
from ecsctl.serializers.serialize_log import deserialize_log_line


def test_deserialize_log_line_returns_a_log_line_from_aws_log_event():
    # Given
    event = {
        "logStreamName": "name",
        "timestamp": 12345,
        "message": "log message",
        "ingestionTime": 12345,
        "eventId": 1,
    }

    # When
    log_line = deserialize_log_line(event)

    # Then
    assert log_line == LogLine("name", 12345, "log message", 12345, 1)

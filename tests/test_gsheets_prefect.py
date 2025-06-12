from pipelines.gsheets_prefect import is_within_asx_hours
from unittest.mock import patch
from datetime import datetime
from zoneinfo import ZoneInfo


def test_is_within_asx_hours_weekend():
    # Saturday
    test_dt = datetime(2024, 6, 8, 12, 0, tzinfo=ZoneInfo("Australia/Sydney"))
    with patch("pipelines.gsheets_prefect.datetime") as mock_datetime:
        mock_datetime.now.return_value = test_dt
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        assert not is_within_asx_hours()


def test_is_within_asx_hours_open():
    # Monday, 11am
    test_dt = datetime(2024, 6, 10, 11, 0, tzinfo=ZoneInfo("Australia/Sydney"))
    with patch("pipelines.gsheets_prefect.datetime") as mock_datetime:
        mock_datetime.now.return_value = test_dt
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        assert is_within_asx_hours()
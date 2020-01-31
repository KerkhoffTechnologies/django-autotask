from django.test import TestCase
from django.utils import timezone
from django.test import override_settings
from datetime import timedelta
from atws.wrapper import Wrapper
from freezegun import freeze_time
from datetime import datetime
import pytz
from djautotask.tests import mocks
from djautotask.models import TimeEntry


class TestTicket(TestCase):
    pass


class TestTimeEntry(TestCase):

    def setUp(self):
        super().setUp()
        mocks.init_api_connection(Wrapper)

    @freeze_time("2020-02-02 13:20:00", tz_offset=-8)
    def test_get_entered_time_has_end_date_time(self):
        """
        Test that get_entered_time returns a time entry's end_date_time.
        """
        end_time = timezone.now() + timedelta(hours=1)
        time_entry = TimeEntry()
        time_entry.start_date_time = timezone.now()
        time_entry.end_date_time = end_time

        self.assertEqual(time_entry.get_entered_time(), end_time)

    def assert_get_entered_time_date_worked(self, local_midnight_utc):
        """
        Verify that the time of date_worked is set to midnight local time.
        Autotask gives us date_worked's time as EST 00:00:00 which then
        gets converted to UTC 05:00:00.
        """
        date_worked = datetime(2020, 2, 2, 5, 0, 0, tzinfo=pytz.utc)
        time_entry = TimeEntry()
        time_entry.date_worked = date_worked

        self.assertEqual(time_entry.get_entered_time(), local_midnight_utc)

    @override_settings(TIME_ZONE='America/Vancouver')
    def test_get_entered_time_date_worked_pst(self):

        # Since Django converts UTC datetimes to local time in the
        # templates so we'll just compare UTC time here.
        local_midnight = datetime(2020, 2, 2, 8, 0, 0, tzinfo=timezone.utc)
        self.assert_get_entered_time_date_worked(local_midnight)

    @override_settings(TIME_ZONE='America/New_York')
    def test_get_entered_time_date_worked_est(self):
        local_midnight_utc = datetime(2020, 2, 2, 5, 0, 0, tzinfo=pytz.utc)
        self.assert_get_entered_time_date_worked(local_midnight_utc)

    @override_settings(TIME_ZONE='Australia/Sydney')
    def test_get_entered_time_date_worked_australia(self):
        local_midnight_utc = datetime(2020, 2, 2, 13, 0, 0, tzinfo=pytz.utc)
        self.assert_get_entered_time_date_worked(local_midnight_utc)

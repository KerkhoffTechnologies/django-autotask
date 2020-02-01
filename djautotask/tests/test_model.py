from django.test import TestCase
from django.utils import timezone
from django.test import override_settings
from datetime import timedelta
from atws.wrapper import Wrapper
import pytz
from djautotask.tests import mocks
from djautotask.models import TimeEntry, OFFSET_TIMEZONE


class TestTicket(TestCase):
    pass


class TestTimeEntry(TestCase):

    def setUp(self):
        super().setUp()
        mocks.init_api_connection(Wrapper)

    def test_get_entered_time_has_end_date_time(self):
        """
        Test that get_entered_time returns a time entry's end_date_time.
        """
        end_time = timezone.now() + timedelta(hours=1)
        time_entry = TimeEntry()
        time_entry.start_date_time = timezone.now()
        time_entry.end_date_time = end_time

        self.assertEqual(time_entry.get_entered_time(), end_time)

    def assert_get_entered_time_date_worked(self, local_midnight):
        """
        Verify that the time of date_worked is set to midnight local time.
        Autotask gives us date_worked's time as EST 00:00:00 which then
        gets converted to UTC 05:00:00.
        """
        midnight_est = timezone.localtime(
            timezone=pytz.timezone(OFFSET_TIMEZONE)
        ).replace(
            month=local_midnight.month, day=local_midnight.day,
            hour=0, minute=0, second=0, microsecond=0
        )
        # Convert to UTC just like Django does when we receive Autotask data.
        date_worked = midnight_est.astimezone(pytz.utc)
        time_entry = TimeEntry()
        time_entry.date_worked = date_worked

        # Convert our local datetime to UTC since that is
        # what get_entered_time returns.
        local_midnight_utc = local_midnight.astimezone(pytz.utc)
        self.assertEqual(time_entry.get_entered_time(), local_midnight_utc)

    @override_settings(TIME_ZONE='America/Vancouver')
    def test_get_entered_time_date_worked_pst(self):

        local_midnight = timezone.localtime().replace(
            hour=0, minute=0, second=0, microsecond=0)

        self.assert_get_entered_time_date_worked(local_midnight)

    @override_settings(TIME_ZONE='America/New_York')
    def test_get_entered_time_date_worked_est(self):

        local_midnight = timezone.localtime().replace(
            hour=0, minute=0, second=0, microsecond=0)

        self.assert_get_entered_time_date_worked(local_midnight)

    @override_settings(TIME_ZONE='Australia/Sydney')
    def test_get_entered_time_date_worked_australia(self):

        local_midnight = timezone.localtime().replace(
            hour=0, minute=0, second=0, microsecond=0)

        self.assert_get_entered_time_date_worked(local_midnight)

    @override_settings(TIME_ZONE='Europe/Paris')
    def test_get_entered_time_date_worked_paris(self):

        local_midnight = timezone.localtime().replace(
            hour=0, minute=0, second=0, microsecond=0)

        self.assert_get_entered_time_date_worked(local_midnight)

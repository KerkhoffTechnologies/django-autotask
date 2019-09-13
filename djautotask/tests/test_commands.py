import io
from atws.wrapper import Wrapper
from django.core.management import call_command
from django.test import TestCase
from djautotask.tests import fixtures, mocks, fixture_utils
from djautotask import models


def sync_summary(class_name, created_count):
    return '{} Sync Summary - Created: {}, Updated: 0'.format(
        class_name, created_count
    )


def full_sync_summary(class_name, deleted_count):
    return '{} Sync Summary - Created: 0, Updated: 0, Deleted: {}'.format(
        class_name, deleted_count
    )


def slug_to_title(slug):
    return slug.title().replace('_', ' ')


def run_sync_command(full_option=False, command_name=None):
    out = io.StringIO()
    args = ['atsync']

    if command_name:
        args.append(command_name)

    if full_option:
        args.append('--full')

    call_command(*args, stdout=out)

    return out


class AbstractBaseSyncTest(object):

    def setUp(self):
        mocks.init_api_connection(Wrapper)

    def _title_for_at_object(self, at_object):
        return at_object.title().replace('_', ' ')

    def get_return_value(self, at_object, fixture_list):
        return fixture_utils.generate_objects(at_object.title(), fixture_list)

    def init_sync_command(self, mock_call, fixture_list, at_object,
                          full_option=False):
        return_value = self.get_return_value(at_object, fixture_list)
        mock_call(return_value)

        output = run_sync_command(full_option, at_object)
        return output

    def _test_sync(self):
        out = self.init_sync_command(*self.args)
        obj_title = self._title_for_at_object(self.args[-1])

        self.assertIn(obj_title, out.getvalue().strip())

    def test_full_sync(self):
        out = self.init_sync_command(*self.args)

        mock_call, fixture_list, at_object = self.args
        args = [
            mock_call,
            [],
            at_object,
        ]

        out = self.init_sync_command(*args, full_option=True)

        obj_label = self._title_for_at_object(at_object)
        msg_tmpl = '{} Sync Summary - Created: 0, Updated: 0, Deleted: {}'

        value_count = len(fixture_list)

        msg = msg_tmpl.format(obj_label, value_count)

        self.assertEqual(msg, out.getvalue().strip())


class TestSyncTicketCommand(AbstractBaseSyncTest, TestCase):
    command_name = 'ticket'
    args = (
        mocks.service_ticket_api_call,
        fixtures.API_SERVICE_TICKET_LIST,
        'ticket',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_ticket_statuses()


class TestSyncTicketStatusCommand(AbstractBaseSyncTest, TestCase):
    command_name = 'ticket_status'

    def get_return_value(self, at_object, fixture_list):
        field_info = fixture_utils.generate_picklist_objects(
            'Status', fixture_list)

        return field_info

    args = (
        mocks.service_ticket_status_api_call,
        fixtures.API_TICKET_STATUS_LIST,
        'ticket_status',

    )


class TestSyncAllCommand(TestCase):

    def setUp(self):
        super().setUp()
        mocks.init_api_connection(Wrapper)

        ticket = fixture_utils.generate_objects(
            'Ticket', fixtures.API_SERVICE_TICKET_LIST)
        ticket_status = fixture_utils.generate_picklist_objects(
            'Status', fixtures.API_TICKET_STATUS_LIST
        )

        mocks.service_ticket_api_call(ticket)
        mocks.service_ticket_status_api_call(ticket_status)

        sync_test_cases = [
            TestSyncTicketCommand,
            TestSyncTicketStatusCommand,
        ]

        self.test_args = []

        for test_case in sync_test_cases:
            self.test_args.append(test_case.args)

    def test_partial_sync(self):
        """
        Test the command to run a sync of all objects without
        the --full argument.
        """
        output = run_sync_command()

        for apicall, fixture, at_object in self.test_args:
            summary = sync_summary(slug_to_title(at_object), len(fixture))
            self.assertIn(summary, output.getvalue().strip())

        self.assertEqual(models.Ticket.objects.all().count(),
                         len(fixtures.API_SERVICE_TICKET_LIST))

    def test_full_sync(self):
        """Test the command to run a full sync of all objects."""
        at_object_map = {
            'ticket_status': models.TicketStatus,
            'ticket': models.Ticket,
        }
        run_sync_command()
        pre_full_sync_counts = {}

        empty_api_call = fixture_utils.generate_picklist_objects('Status', [])
        mocks.service_ticket_status_api_call(empty_api_call)

        for key, model_class in at_object_map.items():
            pre_full_sync_counts[key] = model_class.objects.all().count()

        output = run_sync_command(full_option=True)
        for apicall, fixture, at_object in self.test_args:
            summary = full_sync_summary(
                slug_to_title(at_object),
                pre_full_sync_counts[at_object.lower()]
            )
            self.assertIn(summary, output.getvalue().strip())

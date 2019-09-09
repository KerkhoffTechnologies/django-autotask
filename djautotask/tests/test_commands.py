import io
from atws.wrapper import Wrapper
from django.core.management import call_command
from django.test import TestCase
from djautotask.tests import fixtures, mocks, fixture_utils


def sync_summary(class_name, created_count):
    return '{} Sync Summary - Created: {}, Updated: 0'.format(
        class_name, created_count
    )


def full_sync_summary(class_name, deleted_count):
    return '{} Sync Summary - Created: 0, Updated: 0, Deleted: {}'.format(
        class_name, deleted_count
    )


class AbstractBaseSyncTest(object):

    def setUp(self):
        mocks.init_api_connection(Wrapper)

    def _title_for_at_object(self, at_object):
        return at_object.title().replace('_', ' ')

    def get_return_value(self, at_object, fixture_list):
        return fixture_utils.generate_objects(at_object, fixture_list)

    def _test_sync(self, mock_call, fixture_list, at_object,
                   full_option=False):

        model_class = at_object.title().replace('_', '')
        return_value = self.get_return_value(model_class, fixture_list)
        mock_call(return_value)

        out = io.StringIO()
        args = ['atsync', at_object]
        if full_option:
            args.append('--full')
        call_command(*args, stdout=out)
        return out

    def _nope_test_sync(self):
        out = self._test_sync(*self.args)
        obj_title = self._title_for_at_object(self.args[-1])

        self.assertIn(obj_title, out.getvalue().strip())

    def test_full_sync(self):
        self._nope_test_sync()

        mock_call, fixture_list, at_object = self.args
        print(fixture_list)
        args = [
            mock_call,
            [],
            at_object,
        ]

        out = self._test_sync(*args, full_option=True)
        obj_label = self._title_for_at_object(at_object)
        msg_tmpl = '{} Sync Summary - Created: 0, Updated: 0, Deleted: {}'

        value_count = len(fixture_list)

        msg = msg_tmpl.format(obj_label, value_count)

        self.assertEqual(msg, out.getvalue().strip())


class TestSyncTicketCommand(AbstractBaseSyncTest, TestCase):
    args = (
        mocks.service_ticket_api_call,
        [fixtures.API_SERVICE_TICKET],
        'ticket',
    )


class TestSyncTicketStatusCommand(AbstractBaseSyncTest, TestCase):

    def get_return_value(self, at_object, fixture_list):
        field_info = fixture_utils.generate_picklist_objects(
            'Status', fixture_list)

        return field_info

    args = (
        mocks.service_ticket_status_api_call,
        fixtures.API_TICKET_STATUS_LIST,
        'ticket_status',
    )

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
        return at_object.replace('_', ' ')

    def _test_sync(self, mock_call, at_object, fixture_list,
                   full_option=False):

        return_value = fixture_utils.generate_objects(at_object, fixture_list)
        mock_call(return_value)

        out = io.StringIO()
        args = ['atsync', at_object.lower()]
        if full_option:
            args.append('--full')
        call_command(*args, stdout=out)
        return out

    def test_sync(self):

        out = self._test_sync(*self.args)
        obj_title = self._title_for_at_object(self.args[1])

        self.assertIn(obj_title, out.getvalue().strip())

    def test_full_sync(self):
        self.test_sync()
        mock_call, at_object, fixture_list = self.args
        args = [
            mock_call,
            at_object,
            []
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
        'Ticket',
        [fixtures.API_SERVICE_TICKET]
    )

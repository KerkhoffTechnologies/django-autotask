from django.urls import reverse
from django.test import Client, TestCase

from djautotask.models import Ticket
from djautotask.tests import fixtures, mocks, fixture_utils


class TestCallBackView(TestCase):
    def post_data(self):
        client = Client()
        body = b'id=7865&number=T20191029.0002&status=New&created_datetime=' \
               b'2019-10-29T14:14:47.64300000-04:00:00&last_activity_dateti' \
               b'me=2019-10-30T15:06:38.58300000-04:00:00'

        return client.post(
            reverse('djautotask:callback'),
            body,
            content_type='application/x-www-form-urlencoded'
        )

    def assert_fields(self, instance, entity):
        self.assertEqual(instance.description, entity['description'])

    def _test_synced(self, entity):
        response = self.post_data()

        instances = list(Ticket.objects.all())
        instance = Ticket.objects.all()[0]

        self.assert_fields(instance, entity)
        self.assertEqual(instance.id, entity['id'])
        self.assertEqual(len(instances), 1)
        self.assertEqual(response.status_code, 204)

    def test_add(self):
        self.assertEqual(Ticket.objects.count(), 0)

        fixture_utils.init_statuses()
        _, patch = mocks.service_api_get_ticket_call(fixtures.API_TICKET_BY_ID)
        _, _checklist_patch = mocks.create_mock_call(
            "djautotask.sync.TicketChecklistItemsSynchronizer.sync_items",
            None
        )

        self._test_synced(fixtures.API_TICKET_BY_ID['item'])
        patch.stop()
        _checklist_patch.stop()

    def test_update(self):
        fixture_utils.init_statuses()
        fixture_utils.init_tickets()

        self.assertEqual(Ticket.objects.count(), 1)
        # Change the description of the local record to make our test
        # meaningful.
        t = Ticket.objects.get(id=100)
        t.description = 'foobar'
        t.save()
        _, patch = mocks.service_api_get_ticket_call(fixtures.API_TICKET_BY_ID)
        _, _checklist_patch = mocks.create_mock_call(
            "djautotask.sync.TicketChecklistItemsSynchronizer.sync_items",
            None
        )

        self._test_synced(fixtures.API_TICKET_BY_ID['item'])
        patch.stop()
        _checklist_patch.stop()

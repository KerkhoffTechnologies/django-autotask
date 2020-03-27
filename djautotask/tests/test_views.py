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
        self.assertEqual(instance.description, entity['Description'])

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
        test_instance = fixture_utils.generate_objects(
            'Ticket', fixtures.API_TICKET_LIST)
        _, patch = mocks.create_mock_call(
            mocks.WRAPPER_QUERY_METHOD, test_instance)

        self._test_synced(fixtures.API_TICKET)
        patch.stop()

    def test_update(self):
        fixture_utils.init_statuses()
        fixture_utils.init_tickets()

        self.assertEqual(Ticket.objects.count(), 1)
        # Change the description of the local record to make our test
        # meaningful.
        t = Ticket.objects.get(id=7688)
        t.description = 'foobar'
        t.save()
        test_instance = fixture_utils.generate_objects(
            'Ticket', fixtures.API_TICKET_LIST)
        _, patch = mocks.create_mock_call(
            mocks.WRAPPER_QUERY_METHOD, test_instance)

        self._test_synced(fixtures.API_TICKET)
        patch.stop()

from django.test import TestCase
from atws.wrapper import Wrapper
from dateutil.parser import parse

from djautotask.models import Ticket, TicketStatus, Resource, SyncJob
from djautotask import sync
from djautotask.tests import fixtures, mocks, fixture_utils


def assert_sync_job(model_class):
    qset = SyncJob.objects.filter(entity_name=model_class.__name__)
    assert qset.exists()


class TestTicketSynchronizer(TestCase):

    def setUp(self):
        super().setUp()

        mocks.init_api_connection(Wrapper)

        fixture_utils.init_ticket_statuses()
        fixture_utils.init_resources()
        fixture_utils.init_tickets()

    def _assert_sync(self, instance, object_data):

        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.title, object_data['Title'])
        self.assertEqual(instance.ticket_number, object_data['TicketNumber'])
        self.assertEqual(instance.completed_date,
                         parse(object_data['CompletedDate']))
        self.assertEqual(instance.create_date,
                         parse(object_data['CreateDate']))
        self.assertEqual(instance.description, object_data['Description'])
        self.assertEqual(instance.due_date_time,
                         parse(object_data['DueDateTime']))
        self.assertEqual(instance.estimated_hours,
                         object_data['EstimatedHours'])
        self.assertEqual(instance.last_activity_date,
                         parse(object_data['LastActivityDate']))
        self.assertEqual(instance.status.value, str(object_data['Status']))
        self.assertEqual(instance.assigned_resource.id,
                         object_data['AssignedResourceID'])

    def test_sync_ticket(self):
        """
        Test to ensure ticket synchronizer saves a Ticket instance locally.
        """
        self.assertGreater(Ticket.objects.all().count(), 0)

        object_data = fixtures.API_SERVICE_TICKET
        instance = Ticket.objects.get(id=object_data['id'])

        self._assert_sync(instance, object_data)
        assert_sync_job(Ticket)

    def test_delete_stale_tickets(self):
        """
        Local ticket should be deleted if not returned during a full sync
        """
        ticket_id = fixtures.API_SERVICE_TICKET['id']
        ticket_qset = Ticket.objects.filter(id=ticket_id)
        self.assertEqual(ticket_qset.count(), 1)

        mocks.service_ticket_api_call([])

        synchronizer = sync.TicketSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(ticket_qset.count(), 0)


class TestTicketStatusSynchronizer(TestCase):

    def setUp(self):
        super().setUp()

        mocks.init_api_connection(Wrapper)
        fixture_utils.init_ticket_statuses()

    def _assert_sync(self, instance, object_data):

        self.assertEqual(instance.value, str(object_data['Value']))
        self.assertEqual(instance.label, object_data['Label'])
        self.assertEqual(
            instance.is_default_value, object_data['IsDefaultValue'])
        self.assertEqual(instance.sort_order, object_data['SortOrder'])
        self.assertEqual(instance.parent_value, object_data['ParentValue'])
        self.assertEqual(instance.is_active, object_data['IsActive'])
        self.assertEqual(instance.is_system, object_data['IsSystem'])

    def test_sync_ticket_status(self):
        """
        Test to ensure ticket status synchronizer saves a TicketStatus
        instance locally.
        """
        instance_dict = {}
        for status in fixtures.API_TICKET_STATUS_LIST:
            instance_dict[str(status['Value'])] = status

        for instance in TicketStatus.objects.all():
            object_data = instance_dict[instance.value]

            self._assert_sync(instance, object_data)

        assert_sync_job(TicketStatus)

    def test_delete_stale_ticket_statuses(self):
        """
        Test that ticket status is deleted if not returned during a full sync.
        """
        status_qset = TicketStatus.objects.all()
        self.assertEqual(status_qset.count(), 4)

        empty_api_call = fixture_utils.generate_picklist_objects('Status', [])
        mocks.service_ticket_status_api_call(empty_api_call)

        synchronizer = sync.TicketStatusSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(status_qset.count(), 0)


class TestResourceSynchronizer(TestCase):

    def setUp(self):
        super().setUp()

        mocks.init_api_connection(Wrapper)
        fixture_utils.init_resources()

    def _assert_sync(self, instance, object_data):

        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.user_name, object_data['UserName'])
        self.assertEqual(instance.first_name, object_data['FirstName'])
        self.assertEqual(instance.last_name, object_data['LastName'])
        self.assertEqual(instance.email, object_data['Email'])
        self.assertEqual(instance.active, object_data['Active'])

    def test_sync_resource(self):
        """
        Test to ensure resource synchronizer saves a Resource
        instance locally.
        """
        self.assertGreater(Resource.objects.all().count(), 0)

        object_data = fixtures.API_RESOURCE
        instance = Resource.objects.get(id=object_data['id'])

        self._assert_sync(instance, object_data)
        assert_sync_job(Resource)

    def test_delete_stale_resources(self):
        """
        Test that resource is removed if not fetched from the API during a
        full sync.
        """
        resource_qset = Resource.objects.all()
        self.assertEqual(resource_qset.count(), 1)

        mocks.resource_api_call([])

        synchronizer = sync.ResourceSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(resource_qset.count(), 0)

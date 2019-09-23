from django.test import TestCase
from atws.wrapper import Wrapper
from dateutil.parser import parse

from djautotask.models import Ticket, TicketStatus, Resource, SyncJob, \
    TicketSecondaryResource, TicketPriority, Queue, Account
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
        self.assertEqual(instance.status.id, object_data['Status'])
        self.assertEqual(instance.assigned_resource.id,
                         object_data['AssignedResourceID'])

    def test_sync_ticket(self):
        """
        Test to ensure ticket synchronizer saves a Ticket instance locally.
        """
        self.assertGreater(Ticket.objects.all().count(), 0)

        object_data = fixtures.API_TICKET
        instance = Ticket.objects.get(id=object_data['id'])

        self._assert_sync(instance, object_data)
        assert_sync_job(Ticket)

    def test_delete_stale_tickets(self):
        """
        Local ticket should be deleted if not returned during a full sync
        """
        ticket_id = fixtures.API_TICKET['id']
        ticket_qset = Ticket.objects.filter(id=ticket_id)
        self.assertEqual(ticket_qset.count(), 1)

        mocks.ticket_api_call([])

        synchronizer = sync.TicketSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(ticket_qset.count(), 0)


class AbstractPicklistSynchronizer(object):

    def setUp(self):
        mocks.init_api_connection(Wrapper)

    def _assert_sync(self, instance, object_data):
        self.assertEqual(instance.id, object_data['Value'])
        self.assertEqual(instance.label, object_data['Label'])
        self.assertEqual(
            instance.is_default_value, object_data['IsDefaultValue'])
        self.assertEqual(instance.sort_order, object_data['SortOrder'])
        self.assertEqual(instance.parent_value, object_data['ParentValue'])
        self.assertEqual(instance.is_active, object_data['IsActive'])
        self.assertEqual(instance.is_system, object_data['IsSystem'])


class TestTicketStatusSynchronizer(AbstractPicklistSynchronizer, TestCase):

    def setUp(self):
        super().setUp()
        fixture_utils.init_ticket_statuses()

    def test_sync_ticket_status(self):
        """
        Test to ensure ticket status synchronizer saves a TicketStatus
        instance locally.
        """
        instance_dict = {}
        for status in fixtures.API_TICKET_STATUS_LIST:
            instance_dict[status['Value']] = status

        for instance in TicketStatus.objects.all():
            object_data = instance_dict[instance.id]

            self._assert_sync(instance, object_data)

        assert_sync_job(TicketStatus)

    def test_delete_stale_ticket_statuses(self):
        """
        Test that ticket status is deleted if not returned during a full sync.
        """
        status_qset = TicketStatus.objects.all()
        self.assertEqual(status_qset.count(), 4)

        empty_api_call = fixture_utils.generate_picklist_objects('Status', [])
        mocks.ticket_status_api_call(empty_api_call)

        synchronizer = sync.TicketStatusSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(status_qset.count(), 0)


class TestTicketPrioritySynchronizer(AbstractPicklistSynchronizer, TestCase):

    def setUp(self):
        super().setUp()
        fixture_utils.init_ticket_priorities()

    def test_sync_ticket_priority(self):
        instance_dict = {}
        for priority in fixtures.API_TICKET_PRIORITY_LIST:
            instance_dict[priority['Value']] = priority

        for instance in TicketPriority.objects.all():
            object_data = instance_dict[instance.id]

            self._assert_sync(instance, object_data)

        assert_sync_job(TicketPriority)

    def test_delete_stale_ticket_priorities(self):

        priority_qset = TicketPriority.objects.all()
        self.assertEqual(priority_qset.count(), 2)

        empty_api_call = \
            fixture_utils.generate_picklist_objects('Priority', [])
        mocks.ticket_priority_api_call(empty_api_call)

        synchronizer = sync.TicketPrioritySynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(priority_qset.count(), 0)


class TestQueueSynchronizer(AbstractPicklistSynchronizer, TestCase):

    def setUp(self):
        super().setUp()
        fixture_utils.init_queues()

    def test_sync_queue(self):
        instance_dict = {}
        for queue in fixtures.API_QUEUE_LIST:
            instance_dict[queue['Value']] = queue

        for instance in Queue.objects.all():
            object_data = instance_dict[instance.id]

            self._assert_sync(instance, object_data)

        assert_sync_job(Queue)

    def test_delete_stale_queue(self):

        queue_qset = Queue.objects.all()
        self.assertEqual(queue_qset.count(), 3)

        empty_api_call = fixture_utils.generate_picklist_objects('QueueID', [])
        mocks.queue_api_call(empty_api_call)

        synchronizer = sync.QueueSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(queue_qset.count(), 0)


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


class TestTicketSecondaryResourceSynchronizer(TestCase):

    def setUp(self):
        super().setUp()
        fixture_utils.init_resources()
        fixture_utils.init_tickets()
        fixture_utils.init_secondary_resources()

    def _assert_sync(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.ticket.id, object_data['TicketID'])
        self.assertEqual(instance.resource.id, object_data['ResourceID'])

    def test_sync_ticket_secondary_resource(self):
        self.assertGreater(TicketSecondaryResource.objects.all().count(), 0)
        object_data = fixtures.API_SECONDARY_RESOURCE_LIST[0]
        instance = TicketSecondaryResource.objects.get(id=object_data['id'])

        self._assert_sync(instance, object_data)
        assert_sync_job(TicketSecondaryResource)

    def test_delete_ticket_secondary_resource(self):
        secondary_resources_qset = TicketSecondaryResource.objects.all()
        self.assertEqual(secondary_resources_qset.count(), 2)

        mocks.secondary_resource_api_call([])

        synchronizer = sync.TicketSecondaryResourceSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(secondary_resources_qset.count(), 0)


class TestAccountSynchronizer(TestCase):

    def setUp(self):
        super().setUp()
        fixture_utils.init_accounts()

    def _assert_sync(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.name, object_data['AccountName'])
        self.assertEqual(instance.number, str(object_data['AccountNumber']))
        self.assertEqual(instance.active, object_data['Active'])
        self.assertEqual(instance.last_activity_date,
                         parse(object_data['LastActivityDate']))

    def test_sync_account(self):
        self.assertGreater(Account.objects.all().count(), 0)
        object_data = fixtures.API_ACCOUNT_LIST[0]
        instance = Account.objects.get(id=object_data['id'])

        self._assert_sync(instance, object_data)
        assert_sync_job(Account)

    def test_delete_stale_account(self):
        account_qset = Account.objects.all()
        self.assertEqual(account_qset.count(), 1)

        mocks.account_api_call([])

        synchronizer = sync.AccountSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(account_qset.count(), 0)

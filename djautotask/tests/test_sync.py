from django.test import TestCase
from atws.wrapper import Wrapper

from djautotask.models import Ticket, TicketStatus, Resource, SyncJob, \
    TicketSecondaryResource, TicketPriority, Queue, Account, Project, \
    ProjectType, ProjectStatus, TicketCategory, Source, IssueType, \
    SubIssueType, TicketType, DisplayColor
from djautotask import sync
from djautotask.tests import fixtures, mocks, fixture_utils


def assert_sync_job(model_class):
    qset = SyncJob.objects.filter(entity_name=model_class.__name__)
    assert qset.exists()


class AbstractSynchronizer(object):

    def setUp(self):
        mocks.generate_initial_api_result(
            fixture_utils.manage_client_service_query_return_data
        )


class TestTicketSynchronizer(AbstractSynchronizer, TestCase):

    def setUp(self):
        super().setUp()

        fixture_utils.init_ticket_statuses()
        fixture_utils.init_resources()
        fixture_utils.init_tickets()

    def _assert_sync(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.title, object_data['Title'])
        self.assertEqual(instance.ticket_number, object_data['TicketNumber'])
        self.assertEqual(instance.completed_date, object_data['CompletedDate'])
        self.assertEqual(instance.create_date, object_data['CreateDate'])
        self.assertEqual(instance.description, object_data['Description'])
        self.assertEqual(instance.due_date_time, object_data['DueDateTime'])
        self.assertEqual(instance.estimated_hours,
                         object_data['EstimatedHours'])
        self.assertEqual(instance.last_activity_date,
                         object_data['LastActivityDate'])
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

        mocks.api_query_call([])

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

    def test_evaluate_sync(self):
        """
        Test to ensure given picklist synchronizer saves its instance locally.
        """
        instance_dict = {}
        for item in self.fixture:
            instance_dict[item['Value']] = item

        for instance in self.model_class.objects.all():
            object_data = instance_dict[instance.id]

            self._assert_sync(instance, object_data)

        assert_sync_job(self.model_class)

    def test_evaluate_objects_deleted(self):
        """
        Test that a give object is deleted if not returned during a full sync.
        """
        qset = self.model_class.objects.all()
        self.assertEqual(qset.count(), len(self.fixture))

        # Ensure that the get_field_info method returns no API objects
        # so that the full sync will remove the existing objects in the DB.
        mocks.get_field_info_api_calls()

        synchronizer = self.synchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(qset.count(), 0)


class TestTicketStatusSynchronizer(AbstractPicklistSynchronizer, TestCase):
    model_class = TicketStatus
    fixture = fixtures.API_TICKET_STATUS_LIST
    synchronizer = sync.TicketStatusSynchronizer

    def setUp(self):
        super().setUp()
        fixture_utils.init_ticket_statuses()


class TestTicketPrioritySynchronizer(AbstractPicklistSynchronizer, TestCase):
    model_class = TicketPriority
    fixture = fixtures.API_TICKET_PRIORITY_LIST
    synchronizer = sync.TicketPrioritySynchronizer

    def setUp(self):
        super().setUp()
        fixture_utils.init_ticket_priorities()


class TestQueueSynchronizer(AbstractPicklistSynchronizer, TestCase):
    model_class = Queue
    fixture = fixtures.API_QUEUE_LIST
    synchronizer = sync.QueueSynchronizer

    def setUp(self):
        super().setUp()
        fixture_utils.init_queues()


class TestProjectStatusSynchronizer(AbstractPicklistSynchronizer, TestCase):
    model_class = ProjectStatus
    fixture = fixtures.API_PROJECT_STATUS_LIST
    synchronizer = sync.ProjectStatusSynchronizer

    def setUp(self):
        super().setUp()
        fixture_utils.init_project_statuses()


class TestProjectTypeSynchronizer(AbstractPicklistSynchronizer, TestCase):
    model_class = ProjectType
    fixture = fixtures.API_PROJECT_TYPE_LIST
    synchronizer = sync.ProjectTypeSynchronizer

    def setUp(self):
        super().setUp()
        fixture_utils.init_project_types()


class TestSourceSynchronizer(AbstractPicklistSynchronizer, TestCase):
    model_class = Source
    fixture = fixtures.API_SOURCE_LIST
    synchronizer = sync.SourceSynchronizer

    def setUp(self):
        super().setUp()
        fixture_utils.init_sources()


class TestIssueTypeSynchronizer(AbstractPicklistSynchronizer, TestCase):
    model_class = IssueType
    fixture = fixtures.API_ISSUE_TYPE_LIST
    synchronizer = sync.IssueTypeSynchronizer

    def setUp(self):
        super().setUp()
        fixture_utils.init_issue_types()


class TestSubIssueTypeSynchronizer(AbstractPicklistSynchronizer, TestCase):
    model_class = SubIssueType
    fixture = fixtures.API_SUB_ISSUE_TYPE_LIST
    synchronizer = sync.SubIssueTypeSynchronizer

    def setUp(self):
        super().setUp()
        fixture_utils.init_sub_issue_types()


class TicketTypeSynchronizer(AbstractPicklistSynchronizer, TestCase):
    model_class = TicketType
    fixture = fixtures.API_TICKET_TYPE_LIST
    synchronizer = sync.TicketTypeSynchronizer

    def setUp(self):
        super().setUp()
        fixture_utils.init_ticket_types()


class DisplayColorSynchronizer(AbstractPicklistSynchronizer, TestCase):
    model_class = DisplayColor
    fixture = fixtures.API_DISPLAY_COLOR_LIST
    synchronizer = sync.DisplayColorSynchronizer

    def setUp(self):
        super().setUp()
        fixture_utils.init_display_colors()


class TestTicketCategorySynchronizer(TestCase):
    model_class = TicketCategory
    fixture = fixtures.API_TICKET_CATEGORY_LIST
    synchronizer = sync.TicketCategorySynchronizer

    def setUp(self):
        super().setUp()
        fixture_utils.init_display_colors()
        fixture_utils.init_ticket_categories()

    def _assert_sync(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.name, object_data['Name'])
        self.assertEqual(instance.active, object_data['Active'])
        self.assertEqual(instance.display_color.id,
                         object_data['DisplayColorRGB'])

    def test_sync_ticket_category(self):
        """
        Test to ensure ticket category synchronizer saves a Ticket Category
        instance locally.
        """
        self.assertGreater(TicketCategory.objects.all().count(), 0)

        object_data = fixtures.API_TICKET_CATEGORY_LIST[0]
        instance = TicketCategory.objects.get(id=object_data['id'])

        self._assert_sync(instance, object_data)
        assert_sync_job(TicketCategory)

    def test_delete_stale_ticket_category(self):
        """
        Test that ticket category is removed if not fetched from the API
        during a full sync.
        """
        ticket_category_qset = TicketCategory.objects.all()
        self.assertEqual(ticket_category_qset.count(), 2)

        mocks.api_query_call([])

        synchronizer = sync.TicketCategorySynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(ticket_category_qset.count(), 0)


class TestResourceSynchronizer(TestCase):

    def setUp(self):
        super().setUp()
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
        Test that  is removed if not fetched from the API during a
        full sync.
        """
        resource_qset = Resource.objects.all()
        self.assertEqual(resource_qset.count(), 1)

        mocks.api_query_call([])

        synchronizer = sync.ResourceSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(resource_qset.count(), 0)


class TestTicketSecondaryResourceSynchronizer(AbstractSynchronizer, TestCase):

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

        mocks.api_query_call([])

        synchronizer = sync.TicketSecondaryResourceSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(secondary_resources_qset.count(), 0)


class TestAccountSynchronizer(AbstractSynchronizer, TestCase):

    def setUp(self):
        super().setUp()
        fixture_utils.init_accounts()

    def _assert_sync(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.name, object_data['AccountName'])
        self.assertEqual(instance.number, str(object_data['AccountNumber']))
        self.assertEqual(instance.active, object_data['Active'])
        self.assertEqual(instance.last_activity_date,
                         object_data['LastActivityDate'])

    def test_sync_account(self):
        self.assertGreater(Account.objects.all().count(), 0)
        object_data = fixtures.API_ACCOUNT_LIST[0]
        instance = Account.objects.get(id=object_data['id'])

        self._assert_sync(instance, object_data)
        assert_sync_job(Account)

    def test_delete_stale_account(self):
        account_qset = Account.objects.all()
        self.assertEqual(account_qset.count(), 1)

        mocks.api_query_call([])

        synchronizer = sync.AccountSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(account_qset.count(), 0)


class TestProjectSynchronizer(AbstractSynchronizer, TestCase):

    def setUp(self):
        super().setUp()
        fixture_utils.init_resources()
        fixture_utils.init_accounts()
        fixture_utils.init_project_statuses()
        fixture_utils.init_project_types()
        fixture_utils.init_projects()

    def _assert_sync(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.name, object_data['ProjectName'])
        self.assertEqual(instance.number, object_data['ProjectNumber'])
        self.assertEqual(instance.description, object_data['Description'])
        self.assertEqual(instance.actual_hours, object_data['ActualHours'])
        self.assertEqual(instance.completed_date,
                         object_data['CompletedDateTime'].date())
        self.assertEqual(instance.completed_percentage,
                         object_data['CompletedPercentage'])
        self.assertEqual(instance.duration, object_data['Duration'])
        self.assertEqual(instance.start_date,
                         object_data['StartDateTime'].date())
        self.assertEqual(instance.end_date,
                         object_data['EndDateTime'].date())
        self.assertEqual(instance.estimated_time, object_data['EstimatedTime'])
        self.assertEqual(instance.last_activity_date_time,
                         object_data['LastActivityDateTime'])
        self.assertEqual(instance.project_lead_resource.id,
                         object_data['ProjectLeadResourceID'])
        self.assertEqual(instance.account.id, object_data['AccountID'])
        self.assertEqual(instance.status.id, object_data['Status'])
        self.assertEqual(instance.type.id, object_data['Type'])

    def test_sync_project(self):
        self.assertGreater(Project.objects.all().count(), 0)
        object_data = fixtures.API_PROJECT_LIST[0]
        instance = Project.objects.get(id=object_data['id'])

        self._assert_sync(instance, object_data)
        assert_sync_job(Project)

    def test_delete_stale_project(self):
        project_qset = Project.objects.all()
        self.assertEqual(project_qset.count(), 1)

        mocks.api_query_call([])

        synchronizer = sync.ProjectSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(project_qset.count(), 0)

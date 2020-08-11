from django.test import TestCase
from atws.wrapper import Wrapper

import random
from copy import deepcopy
from djautotask.models import Ticket, Status, Resource, SyncJob, \
    TicketSecondaryResource, Priority, Queue, Account, Project, \
    ProjectType, ProjectStatus, TicketCategory, Source, IssueType, \
    SubIssueType, TicketType, DisplayColor, LicenseType, Task, \
    TaskSecondaryResource, Phase, TimeEntry, TicketNote, TaskNote, \
    TaskTypeLink, UseType, AllocationCode, Role, Department, \
    ResourceRoleDepartment, ResourceServiceDeskRole, Contract, AccountType, \
    ServiceCall, ServiceCallStatus, AccountPhysicalLocation
from djautotask import sync
from djautotask.utils import DjautotaskSettings
from djautotask.tests import fixtures, mocks, fixture_utils


def assert_sync_job(model_class):
    qset = SyncJob.objects.filter(entity_name=model_class.__name__)
    assert qset.exists()


class TestAssignNullRelationMixin:
    def test_sync_assigns_null_relation(self):
        model_type = self.model_class.__name__
        model_object = self.model_class.objects.first()

        self.assertIsNotNone(model_object.assigned_resource)

        fixture_instance = deepcopy(
            getattr(fixtures, 'API_{}'.format(model_type.upper()))
        )
        fixture_instance.pop('AssignedResourceID')

        object_instance = fixture_utils.generate_objects(
            model_type, [fixture_instance]
        )
        _, patch = mocks.create_mock_call(
            mocks.WRAPPER_QUERY_METHOD, object_instance
        )
        synchronizer = self.sync_class(full=True)
        synchronizer.sync()

        model_object = self.model_class.objects.get(id=model_object.id)
        self.assertIsNone(model_object.assigned_resource)
        patch.stop()


class TestTicketNoteSynchronizer(TestCase):
    def setUp(self):
        super().setUp()
        self.synchronizer = sync.TicketNoteSynchronizer()
        mocks.init_api_connection(Wrapper)
        fixture_utils.init_resources()
        fixture_utils.init_tickets()
        fixture_utils.init_note_types()
        fixture_utils.init_ticket_notes()

    def _assert_sync(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.title, object_data['Title'])
        self.assertEqual(instance.description, object_data['Description'])
        self.assertEqual(
            instance.create_date_time, object_data['CreateDateTime'])
        self.assertEqual(
            instance.last_activity_date, object_data['LastActivityDate'])
        self.assertEqual(instance.ticket.id, object_data['TicketID'])
        self.assertEqual(
            instance.creator_resource.id, object_data['CreatorResourceID'])
        self.assertEqual(instance.note_type.id, object_data['NoteType'])

    def test_sync_ticket_note(self):
        """
        Test to ensure note synchronizer saves a TicketNote instance locally.
        """
        self.assertGreater(TicketNote.objects.all().count(), 0)

        object_data = fixtures.API_TICKET_NOTE
        instance = TicketNote.objects.get(id=object_data['id'])

        self._assert_sync(instance, object_data)
        assert_sync_job(TicketNote)

    def test_delete_stale_ticket_notes(self):
        """
        Local notes should be deleted if not returned during a full sync
        """
        note_id = fixtures.API_TICKET_NOTE['id']
        qs = TicketNote.objects.filter(id=note_id)
        self.assertEqual(qs.count(), 1)

        mocks.api_query_call([])

        synchronizer = sync.TicketNoteSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(qs.count(), 0)


class TestTaskNoteSynchronizer(TestCase):
    def setUp(self):
        super().setUp()
        self.synchronizer = sync.TaskNoteSynchronizer()
        mocks.init_api_connection(Wrapper)
        fixture_utils.init_resources()
        fixture_utils.init_tasks()
        fixture_utils.init_note_types()
        fixture_utils.init_task_notes()

    def _assert_sync(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.title, object_data['Title'])
        self.assertEqual(instance.description, object_data['Description'])
        self.assertEqual(
            instance.create_date_time, object_data['CreateDateTime'])
        self.assertEqual(
            instance.last_activity_date, object_data['LastActivityDate'])
        self.assertEqual(instance.task.id, object_data['TaskID'])
        self.assertEqual(
            instance.creator_resource.id, object_data['CreatorResourceID'])
        self.assertEqual(instance.note_type.id, object_data['NoteType'])

    def test_sync_task_note(self):
        """
        Test to ensure note synchronizer saves a TaskNote instance locally.
        """
        self.assertGreater(TaskNote.objects.all().count(), 0)

        object_data = fixtures.API_TASK_NOTE
        instance = TaskNote.objects.get(id=object_data['id'])

        self._assert_sync(instance, object_data)
        assert_sync_job(TaskNote)

    def test_delete_stale_task_notes(self):
        """
        Local notes should be deleted if not returned during a full sync
        """
        note_id = fixtures.API_TASK_NOTE['id']
        qs = TaskNote.objects.filter(id=note_id)
        self.assertEqual(qs.count(), 1)

        mocks.api_query_call([])

        synchronizer = sync.TaskNoteSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(qs.count(), 0)


class TestTicketSynchronizer(TestAssignNullRelationMixin, TestCase):
    model_class = Ticket
    sync_class = sync.TicketSynchronizer

    def setUp(self):
        super().setUp()
        self.synchronizer = sync.TicketSynchronizer()

        fixture_utils.init_contracts()
        fixture_utils.init_statuses()
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
        self.assertEqual(instance.contract.id, object_data['ContractID'])

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

    def test_fetch_sync_by_id(self):
        test_instance = fixture_utils.generate_objects(
            'Ticket', fixtures.API_TICKET_LIST)
        _, patch = mocks.create_mock_call(
            mocks.WRAPPER_QUERY_METHOD, test_instance)
        result = self.synchronizer.fetch_sync_by_id(fixtures.API_TICKET['id'])
        self._assert_sync(result, fixtures.API_TICKET)
        patch.stop()

    def test_sync_ticket_related_records(self):
        """
        Test to ensure that a ticket will sync related objects,
        in its case notes, and time entries, and secondary resources
        """
        synchronizer = self.sync_class()

        ticket = Ticket.objects.first()
        ticket.status = Status.objects.first()
        time_mock, time_patch = mocks.create_mock_call(
            'djautotask.sync.TimeEntrySynchronizer.fetch_records',
            None
        )
        note_mock, note_patch = mocks.create_mock_call(
            'djautotask.sync.TicketNoteSynchronizer.fetch_records', None)
        resource_mock, resource_patch = mocks.create_mock_call(
            'djautotask.sync.TicketSecondaryResourceSynchronizer.'
            'fetch_records',
            None
        )

        synchronizer.sync_related(ticket)

        self.assertEqual(time_mock.call_count, 1)
        self.assertEqual(note_mock.call_count, 1)
        self.assertEqual(resource_mock.call_count, 1)
        time_patch.stop()
        note_patch.stop()
        resource_patch.stop()


class AbstractPicklistSynchronizer(object):

    def setUp(self):
        mocks.init_api_connection(Wrapper)

    def _assert_sync(self, instance, object_data):
        self.assertEqual(instance.id, object_data['Value'])
        self.assertEqual(instance.label, object_data['Label'])
        self.assertEqual(
            instance.is_default_value, object_data['IsDefaultValue'])
        self.assertEqual(instance.sort_order, object_data['SortOrder'])
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


class TestStatusSynchronizer(AbstractPicklistSynchronizer, TestCase):
    model_class = Status
    fixture = fixtures.API_STATUS_LIST
    synchronizer = sync.StatusSynchronizer

    def setUp(self):
        super().setUp()
        fixture_utils.init_statuses()


class TestPrioritySynchronizer(AbstractPicklistSynchronizer, TestCase):
    model_class = Priority
    fixture = fixtures.API_PRIORITY_LIST
    synchronizer = sync.PrioritySynchronizer

    def setUp(self):
        super().setUp()
        fixture_utils.init_priorities()


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


class TestTicketTypeSynchronizer(AbstractPicklistSynchronizer, TestCase):
    model_class = TicketType
    fixture = fixtures.API_TICKET_TYPE_LIST
    synchronizer = sync.TicketTypeSynchronizer

    def setUp(self):
        super().setUp()
        fixture_utils.init_ticket_types()


class TestDisplayColorSynchronizer(AbstractPicklistSynchronizer, TestCase):
    model_class = DisplayColor
    fixture = fixtures.API_DISPLAY_COLOR_LIST
    synchronizer = sync.DisplayColorSynchronizer

    def setUp(self):
        super().setUp()
        fixture_utils.init_display_colors()


class TestLicenseTypeSynchronizer(AbstractPicklistSynchronizer, TestCase):
    model_class = LicenseType
    fixture = fixtures.API_LICENSE_TYPE_LIST
    synchronizer = sync.LicenseTypeSynchronizer

    def setUp(self):
        super().setUp()
        fixture_utils.init_license_types()


class TestTaskTypeLinkSynchronizer(AbstractPicklistSynchronizer, TestCase):
    model_class = TaskTypeLink
    fixture = fixtures.API_TASK_TYPE_LINK_LIST
    synchronizer = sync.TaskTypeLinkSynchronizer

    def setUp(self):
        super().setUp()
        fixture_utils.init_task_type_links()


class TestUseTypeSynchronizer(AbstractPicklistSynchronizer, TestCase):
    model_class = UseType
    fixture = fixtures.API_USE_TYPE_LIST
    synchronizer = sync.UseTypeSynchronizer

    def setUp(self):
        super().setUp()
        fixture_utils.init_use_types()


class TestServiceCallStatusSynchronizer(AbstractPicklistSynchronizer,
                                        TestCase):
    model_class = ServiceCallStatus
    fixture = fixtures.API_SERVICE_CALL_STATUS_LIST
    synchronizer = sync.ServiceCallStatusSynchronizer

    def setUp(self):
        super().setUp()
        fixture_utils.init_service_call_statuses()


class TestAccountTypeSynchronizer(AbstractPicklistSynchronizer, TestCase):
    model_class = AccountType
    fixture = fixtures.API_ACCOUNT_TYPE_LIST
    synchronizer = sync.AccountTypeSynchronizer

    def setUp(self):
        super().setUp()
        fixture_utils.init_account_types()


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

        mocks.api_query_call([])

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


class TestAccountPhysicalLocationSynchronizer(TestCase):

    def setUp(self):
        super().setUp()
        fixture_utils.init_accounts()
        fixture_utils.init_account_physical_locations()

    def _assert_sync(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.account.id, object_data['AccountID'])
        self.assertEqual(instance.name, object_data['Name'])
        self.assertEqual(instance.active, object_data['Active'])

    def test_sync_account_location(self):
        self.assertGreater(AccountPhysicalLocation.objects.all().count(), 0)
        object_data = fixtures.API_ACCOUNT_PHYSICAL_LOCATION_LIST[0]
        instance = AccountPhysicalLocation.objects.get(id=object_data['id'])

        self._assert_sync(instance, object_data)
        assert_sync_job(Account)

    def test_delete_stale_account_location(self):
        account_qset = AccountPhysicalLocation.objects.all()
        self.assertEqual(account_qset.count(), 1)

        mocks.api_query_call([])

        synchronizer = sync.AccountPhysicalLocationSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(account_qset.count(), 0)


class FilterProjectTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.inactive_status = ProjectStatus.objects.create(
            label='New (Inactive)', is_active=False)
        cls.inactive_project = Project.objects.create(name='Inactive Project')
        cls.inactive_project.status = cls.inactive_status
        cls.inactive_project.save()


class TestProjectSynchronizer(FilterProjectTestCase):

    def setUp(self):
        super().setUp()
        fixture_utils.init_contracts()
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
        self.assertEqual(instance.contract.id, object_data['ContractID'])

    def test_sync_project(self):
        self.assertGreater(Project.objects.all().count(), 0)
        object_data = fixtures.API_PROJECT_LIST[0]
        instance = Project.objects.get(id=object_data['id'])

        self._assert_sync(instance, object_data)
        assert_sync_job(Project)

    def test_delete_stale_project(self):
        project_qset = Project.objects.all()
        self.assertGreater(project_qset.count(), 1)

        mocks.api_query_call([])

        synchronizer = sync.ProjectSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(project_qset.count(), 0)

    def test_sync_filters_projects_in_inactive_status(self):
        """
        Test to ensure that sync does not persist projects in an
        inactive project status.
        """
        project_in_active_status = fixtures.API_PROJECT_LIST[0]
        project_fixture = deepcopy(project_in_active_status)
        project_fixture['id'] = '5'
        project_fixture['Status'] = self.inactive_status.id

        project_instance = fixture_utils.generate_objects(
            'Project', [project_fixture, fixtures.API_PROJECT_LIST[0]]
        )
        _, patch = mocks.create_mock_call(
            mocks.WRAPPER_QUERY_METHOD, project_instance
        )
        synchronizer = sync.ProjectSynchronizer(full=True)
        synchronizer.sync()

        synced_project_ids = Project.objects.values_list('id', flat=True)
        self.assertGreater(Project.objects.all().count(), 0)
        self.assertNotIn(project_fixture['id'], synced_project_ids)
        self.assertIn(project_in_active_status['id'], synced_project_ids)
        patch.stop()

    def test_sync_filters_projects_in_complete_status(self):
        """
        Test to ensure that sync does not persist projects in an
        inactive project status.
        """
        project_in_complete_status = fixtures.API_PROJECT_LIST[0]
        project_fixture = deepcopy(project_in_complete_status)
        project_fixture['id'] = '6'
        # 5 Is the Autotask system complete status
        project_fixture['Status'] = 5

        project_instance = fixture_utils.generate_objects(
            'Project', [project_fixture, fixtures.API_PROJECT_LIST[0]]
        )
        _, patch = mocks.create_mock_call(
            mocks.WRAPPER_QUERY_METHOD, project_instance
        )
        synchronizer = sync.ProjectSynchronizer(full=True)
        synchronizer.sync()

        synced_project_ids = Project.objects.values_list('id', flat=True)
        self.assertGreater(Project.objects.all().count(), 0)
        self.assertNotIn(project_fixture['id'], synced_project_ids)
        self.assertIn(project_in_complete_status['id'], synced_project_ids)
        patch.stop()


class TestTaskSynchronizer(TestAssignNullRelationMixin,
                           FilterProjectTestCase):
    model_class = Task
    sync_class = sync.TaskSynchronizer

    def setUp(self):
        super().setUp()
        mocks.init_api_connection(Wrapper)

        fixture_utils.init_resources()
        fixture_utils.init_statuses()
        fixture_utils.init_priorities()
        fixture_utils.init_project_statuses()
        fixture_utils.init_projects()
        fixture_utils.init_tasks()

    def _assert_sync(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.title, object_data['Title'])
        self.assertEqual(instance.number, object_data['TaskNumber'])
        self.assertEqual(instance.completed_date,
                         object_data['CompletedDateTime'])
        self.assertEqual(instance.create_date, object_data['CreateDateTime'])
        self.assertEqual(instance.start_date, object_data['StartDateTime'])
        self.assertEqual(instance.description, object_data['Description'])
        self.assertEqual(instance.remaining_hours,
                         object_data['RemainingHours'])
        self.assertEqual(instance.estimated_hours,
                         object_data['EstimatedHours'])
        self.assertEqual(instance.last_activity_date,
                         object_data['LastActivityDateTime'])

        self.assertEqual(instance.status.id, object_data['Status'])
        self.assertEqual(instance.priority.id, object_data['PriorityLabel'])
        self.assertEqual(instance.project.id, object_data['ProjectID'])
        self.assertEqual(instance.assigned_resource.id,
                         object_data['AssignedResourceID'])

    def test_sync_task(self):
        """
        Test to ensure task synchronizer saves a Task instance locally.
        """
        self.assertGreater(Task.objects.all().count(), 0)

        object_data = fixtures.API_TASK
        instance = Task.objects.get(id=object_data['id'])

        self._assert_sync(instance, object_data)
        assert_sync_job(Task)

    def test_delete_stale_tasks(self):
        """
        Local task should be deleted if not returned during a full sync
        """
        task_id = fixtures.API_TASK['id']
        task_qset = Task.objects.filter(id=task_id)
        self.assertEqual(task_qset.count(), 1)

        mocks.api_query_call([])

        synchronizer = sync.TaskSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(task_qset.count(), 0)

    def test_sync_filters_tasks_on_inactive_project(self):

        # Add copied task to project in 'Complete' status to ensure it is
        # filtered out during the sync.
        task_fixture = deepcopy(fixtures.API_TASK)
        task_fixture['id'] = '7740'
        task_fixture['ProjectID'] = self.inactive_project.id

        task_instance = fixture_utils.generate_objects(
            'Task', [task_fixture, fixtures.API_TASK]
        )
        _, patch = mocks.create_mock_call(
            mocks.WRAPPER_QUERY_METHOD, task_instance
        )
        synchronizer = sync.TaskSynchronizer(full=True)
        synchronizer.sync()

        synced_task_ids = Task.objects.values_list('id', flat=True)
        self.assertGreater(Task.objects.all().count(), 0)
        self.assertNotIn(task_fixture['id'], synced_task_ids)
        self.assertIn(fixtures.API_TASK['id'], synced_task_ids)
        patch.stop()

    def test_sync_filters_tasks_on_complete_project(self):
        """
        Test to ensure that sync does not persist tasks on a complete project.
        """
        project = Project.objects.create(name='Complete Project')
        project.status = ProjectStatus.objects.get(id=5)
        project.save()

        task_fixture = deepcopy(fixtures.API_TASK)
        task_fixture['id'] = '7741'
        task_fixture['ProjectID'] = project.id

        task_instance = fixture_utils.generate_objects(
            'Task', [task_fixture, fixtures.API_TASK]
        )
        _, patch = mocks.create_mock_call(
            mocks.WRAPPER_QUERY_METHOD, task_instance
        )
        synchronizer = sync.TaskSynchronizer(full=True)
        synchronizer.sync()

        synced_task_ids = Task.objects.values_list('id', flat=True)
        self.assertGreater(Task.objects.all().count(), 0)
        self.assertNotIn(task_fixture['id'], synced_task_ids)
        self.assertIn(fixtures.API_TASK['id'], synced_task_ids)
        patch.stop()


class TestTaskSecondaryResourceSynchronizer(TestCase):

    def setUp(self):
        super().setUp()
        fixture_utils.init_resources()
        fixture_utils.init_tasks()
        fixture_utils.init_task_secondary_resources()

    def _assert_sync(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.resource.id, object_data['ResourceID'])
        self.assertEqual(instance.task.id, object_data['TaskID'])

    def test_sync_task_secondary_resource(self):
        self.assertGreater(TaskSecondaryResource.objects.all().count(), 0)
        object_data = fixtures.API_TASK_SECONDARY_RESOURCE
        instance = TaskSecondaryResource.objects.get(id=object_data['id'])

        self._assert_sync(instance, object_data)
        assert_sync_job(TaskSecondaryResource)

    def test_delete_task_secondary_resource(self):
        secondary_resources_qset = TaskSecondaryResource.objects.all()
        self.assertEqual(secondary_resources_qset.count(), 1)

        mocks.api_query_call([])

        synchronizer = sync.TaskSecondaryResourceSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(secondary_resources_qset.count(), 0)


class TestPhaseSynchronizer(TestCase):

    def setUp(self):
        super().setUp()
        mocks.init_api_connection(Wrapper)

        fixture_utils.init_projects()
        fixture_utils.init_phases()
        fixture_utils.init_tasks()

    def _assert_sync(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.title, object_data['Title'])
        self.assertEqual(instance.start_date, object_data['StartDate'])
        self.assertEqual(instance.description, object_data['Description'])
        self.assertEqual(instance.estimated_hours,
                         object_data['EstimatedHours'])
        self.assertEqual(instance.last_activity_date,
                         object_data['LastActivityDateTime'])
        self.assertEqual(instance.number, object_data['PhaseNumber'])

    def test_sync_phase(self):
        """
        Test to ensure task synchronizer saves a Phase instance locally.
        """
        self.assertGreater(Phase.objects.all().count(), 0)

        object_data = fixtures.API_PHASE
        instance = Phase.objects.get(id=object_data['id'])

        self._assert_sync(instance, object_data)
        assert_sync_job(Phase)

    def test_delete_stale_phases(self):
        """
        Local task should be deleted if not returned during a full sync
        """
        qset = Phase.objects.all()
        self.assertEqual(qset.count(), 1)

        mocks.api_query_call([])

        synchronizer = sync.PhaseSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(qset.count(), 0)


class TestTimeEntrySynchronizer(TestCase):

    def setUp(self):
        super().setUp()
        mocks.init_api_connection(Wrapper)
        fixture_utils.init_resources()
        fixture_utils.init_tickets()

    def _assert_sync(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.date_worked, object_data['DateWorked'])
        self.assertEqual(instance.start_date_time,
                         object_data['StartDateTime'])
        self.assertEqual(instance.end_date_time, object_data['EndDateTime'])
        self.assertEqual(instance.summary_notes, object_data['SummaryNotes'])
        self.assertEqual(instance.internal_notes, object_data['InternalNotes'])
        self.assertEqual(instance.non_billable, object_data['NonBillable'])
        self.assertEqual(instance.hours_worked, object_data['HoursWorked'])
        self.assertEqual(instance.hours_to_bill, object_data['HoursToBill'])
        self.assertEqual(instance.offset_hours, object_data['OffsetHours'])
        self.assertEqual(instance.ticket.id, object_data['TicketID'])
        self.assertEqual(instance.resource.id, object_data['ResourceID'])

    def test_sync_time_entry(self):
        """
        Test to ensure synchronizer saves a time entry instance locally.
        """
        time_entries = fixture_utils.generate_objects(
            'TimeEntry', fixtures.API_TIME_ENTRY_LIST)
        mocks.api_query_call(time_entries)
        synchronizer = sync.TimeEntrySynchronizer()
        synchronizer.sync()

        self.assertGreater(TimeEntry.objects.all().count(), 0)

        object_data = fixtures.API_TIME_ENTRY_TICKET
        instance = TimeEntry.objects.get(id=object_data['id'])

        ticket = Ticket.objects.first()
        ticket.id = object_data['TicketID']
        instance.ticket = ticket

        resource = Resource.objects.first()
        resource.id = object_data['ResourceID']
        instance.resource = resource

        self._assert_sync(instance, object_data)
        assert_sync_job(TimeEntry)

    def test_sync_time_entry_skipped(self):
        """
        Verify that a time entry does not get saved locally if its ticket
        does not already exist in the local database.
        """
        time_entry_count = TimeEntry.objects.all().count()

        synchronizer = sync.TimeEntrySynchronizer(full=True)
        synchronizer.sync()
        sync_job = SyncJob.objects.last()

        # Time entry for time entry ticket is not saved locally
        # and is subsequently removed.
        self.assertEqual(TimeEntry.objects.all().count(), 0)
        self.assertEqual(sync_job.added, 0)
        self.assertEqual(sync_job.updated, 0)
        self.assertEqual(sync_job.deleted, time_entry_count)

    def test_delete_stale_time_entries(self):
        """
        Verify that time entry is deleted if not returned during a full sync
        """
        time_entries = fixture_utils.generate_objects(
            'TimeEntry', fixtures.API_TIME_ENTRY_LIST)
        mocks.api_query_call(time_entries)
        synchronizer = sync.TimeEntrySynchronizer()
        synchronizer.sync()

        qset = TimeEntry.objects.all()
        self.assertEqual(qset.count(), len(fixtures.API_TIME_ENTRY_LIST))

        mocks.api_query_call([])

        synchronizer = sync.TimeEntrySynchronizer(full=True)
        synchronizer.sync()

        qset = TimeEntry.objects.all()
        self.assertEqual(qset.count(), 0)

    def test_batch_queries_creates_multiple_batches(self):
        """
        Verify that build batch query method returns multiple batches
        ticket and task queries.
        """
        max_id_limit = 500
        settings = DjautotaskSettings().get_settings()
        batch_size = settings.get('batch_query_size')

        synchronizer = sync.TimeEntrySynchronizer()
        sync_job = SyncJob.objects.filter(entity_name='TimeEntry')

        # Simulate ticket IDs
        object_ids = random.sample(range(1, max_id_limit), batch_size + 50)
        _, _patch = mocks.create_mock_call(
            'django.db.models.query.QuerySet.values_list', object_ids
        )

        batch_query_list = synchronizer.build_batch_queries(sync_job)

        # With a max batch size of 400, a set of 450 object IDs should result
        # in 4 Query objects being returned in the list. (2 for tickets, 2 for
        # tasks)
        self.assertEqual(len(batch_query_list), 4)

        _patch.stop()

    def test_batch_queries_returns_query_list(self):
        """
        Verify that an empty list is returned when no tickets or
        tasks are present in the database.
        """
        _, _patch = mocks.create_mock_call(
            'django.db.models.query.QuerySet.values_list', []
        )
        synchronizer = sync.TimeEntrySynchronizer()
        sync_job = SyncJob.objects.filter(entity_name='TimeEntry')

        batch_query_list = synchronizer.build_batch_queries(sync_job)

        self.assertEqual(len(batch_query_list), 0)

        _patch.stop()


class TestAllocationCodeSynchronizer(TestCase):

    def setUp(self):
        super().setUp()
        mocks.init_api_connection(Wrapper)
        fixture_utils.init_use_types()
        fixture_utils.init_allocation_codes()

    def _assert_sync(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.name, object_data.get('Name'))
        self.assertEqual(instance.description, object_data.get('Description'))
        self.assertEqual(instance.active, object_data.get('Active'))
        self.assertEqual(instance.use_type.id, object_data.get('UseType'))

    def test_sync_allocation_code(self):

        self.assertGreater(AllocationCode.objects.all().count(), 0)
        object_data = fixtures.API_ALLOCATION_CODE
        instance = AllocationCode.objects.get(id=object_data['id'])

        self._assert_sync(instance, object_data)
        assert_sync_job(AllocationCode)

    def test_delete_allocation_code(self):
        allocation_code_qset = AllocationCode.objects.all()
        self.assertEqual(allocation_code_qset.count(), 1)

        mocks.api_query_call([])

        synchronizer = sync.AllocationCodeSynchronizer(full=True)
        synchronizer.sync()

        self.assertEqual(allocation_code_qset.count(), 0)


class TestRoleSynchronizer(TestCase):
    def setUp(self):
        super().setUp()
        self.synchronizer = sync.RoleSynchronizer()
        fixture_utils.init_roles()

    def _assert_sync(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.name, object_data['Name'])
        self.assertEqual(instance.description, object_data['Description'])
        self.assertEqual(instance.active, object_data['Active'])
        self.assertEqual(instance.hourly_factor, object_data['HourlyFactor'])
        self.assertEqual(instance.hourly_rate, object_data['HourlyRate'])
        self.assertEqual(instance.role_type, object_data['RoleType'])
        self.assertEqual(instance.system_role, object_data['SystemRole'])

    def test_sync_role(self):
        """
        Test to ensure role synchronizer saves a Role instance locally.
        """
        self.assertGreater(Role.objects.all().count(), 0)

        object_data = fixtures.API_ROLE
        instance = Role.objects.get(id=object_data['id'])

        self._assert_sync(instance, object_data)
        assert_sync_job(Role)

    def test_delete_stale_roles(self):
        """
        Local Roles should be deleted if not returned during a full sync
        """
        role_id = fixtures.API_ROLE['id']
        qs = Role.objects.filter(id=role_id)
        self.assertEqual(qs.count(), 1)

        mocks.api_query_call([])

        synchronizer = sync.RoleSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(qs.count(), 0)


class TestDepartmentSynchronizer(TestCase):
    def setUp(self):
        super().setUp()
        self.synchronizer = sync.DepartmentSynchronizer()
        fixture_utils.init_departments()

    def _assert_sync(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.name, object_data['Name'])
        self.assertEqual(instance.description, object_data['Description'])
        self.assertEqual(instance.number, object_data['Number'])

    def test_sync_department(self):
        """
        Test to ensure department synchronizer saves a Department instance
        locally.
        """
        self.assertGreater(Department.objects.all().count(), 0)

        object_data = fixtures.API_DEPARTMENT
        instance = Department.objects.get(id=object_data['id'])

        self._assert_sync(instance, object_data)
        assert_sync_job(Department)

    def test_delete_stale_departments(self):
        """
        Local Departments should be deleted if not returned during a full sync
        """
        department_id = fixtures.API_DEPARTMENT['id']
        qs = Department.objects.filter(id=department_id)
        self.assertEqual(qs.count(), 1)

        mocks.api_query_call([])

        synchronizer = sync.DepartmentSynchronizer(full=True)
        synchronizer.sync()
        self.assertEqual(qs.count(), 0)


class TestResourceRoleDepartmentSynchronizer(TestCase):

    def setUp(self):
        super().setUp()
        mocks.init_api_connection(Wrapper)
        fixture_utils.init_departments()
        fixture_utils.init_roles()
        fixture_utils.init_resources()

    def _assert_sync(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.active, object_data['Active'])
        self.assertEqual(instance.default, object_data['Default'])
        self.assertEqual(instance.department_lead,
                         object_data['DepartmentLead'])
        self.assertEqual(instance.resource.id, object_data['ResourceID'])
        self.assertEqual(instance.role.id, object_data['RoleID'])
        self.assertEqual(instance.department.id, object_data['DepartmentID'])

    def test_sync_resource_role_department(self):
        """
        Test to ensure synchronizer saves an instance locally.
        """
        resource_role_department = fixture_utils.generate_objects(
            'ResourceRoleDepartment',
            fixtures.API_RESOURCE_ROLE_DEPARTMENT_LIST)
        mocks.api_query_call(resource_role_department)
        synchronizer = sync.ResourceRoleDepartmentSynchronizer()
        synchronizer.sync()

        self.assertGreater(ResourceRoleDepartment.objects.all().count(), 0)

        object_data = fixtures.API_RESOURCE_ROLE_DEPARTMENT
        instance = ResourceRoleDepartment.objects.get(id=object_data['id'])

        role = Role.objects.first()
        role.id = object_data['RoleID']
        instance.role = role

        resource = Resource.objects.first()
        resource.id = object_data['ResourceID']
        instance.resource = resource

        department = Department.objects.first()
        department.id = object_data['DepartmentID']
        instance.department = department

        self._assert_sync(instance, object_data)
        assert_sync_job(ResourceRoleDepartment)


class TestResourceServiceDeskRoleSynchronizer(TestCase):

    def setUp(self):
        super().setUp()
        mocks.init_api_connection(Wrapper)
        fixture_utils.init_roles()
        fixture_utils.init_resources()

    def _assert_sync(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.active, object_data['Active'])
        self.assertEqual(instance.default, object_data['Default'])
        self.assertEqual(instance.resource.id, object_data['ResourceID'])
        self.assertEqual(instance.role.id, object_data['RoleID'])

    def test_sync_resource_service_desk_role(self):
        """
        Test to ensure synchronizer saves an instance locally.
        """
        resource_service_desk_role = fixture_utils.generate_objects(
            'ResourceServiceDeskRole',
            fixtures.API_RESOURCE_SERVICE_DESK_ROLE_LIST)
        mocks.api_query_call(resource_service_desk_role)
        synchronizer = sync.ResourceServiceDeskRoleSynchronizer()
        synchronizer.sync()

        self.assertGreater(ResourceServiceDeskRole.objects.all().count(), 0)

        object_data = fixtures.API_RESOURCE_SERVICE_DESK_ROLE
        instance = ResourceServiceDeskRole.objects.get(id=object_data['id'])

        role = Role.objects.first()
        role.id = object_data['RoleID']
        instance.role = role

        resource = Resource.objects.first()
        resource.id = object_data['ResourceID']
        instance.resource = resource

        self._assert_sync(instance, object_data)
        assert_sync_job(ResourceServiceDeskRole)


class TestContractSynchronizer(TestCase):

    def setUp(self):
        super().setUp()
        mocks.init_api_connection(Wrapper)
        fixture_utils.init_accounts()

    def _assert_sync(self, instance, object_data):

        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.name, object_data['ContractName'])
        self.assertEqual(instance.number, object_data['ContractNumber'])
        self.assertEqual(instance.status, str(object_data['Status']))
        self.assertEqual(instance.account.id, object_data['AccountID'])

    def test_sync_contract(self):
        """
        Test to ensure synchronizer saves a contract instance locally.
        """
        contract = fixture_utils.generate_objects(
            'Contract', fixtures.API_CONTRACT_LIST
        )
        mocks.api_query_call(contract)
        synchronizer = sync.ContractSynchronizer()
        synchronizer.sync()

        self.assertGreater((Contract.objects.count()), 0)

        object_data = fixtures.API_CONTRACT
        instance = Contract.objects.get(id=object_data['id'])

        self._assert_sync(instance, object_data)
        assert_sync_job(Contract)


class TestServiceCallSynchronizer(TestCase):

    def setUp(self):
        super().setUp()
        mocks.init_api_connection(Wrapper)
        fixture_utils.init_service_call_statuses()
        fixture_utils.init_resources()
        fixture_utils.init_account_types()
        fixture_utils.init_accounts()

    def _assert_sync(self, instance, object_data):

        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.description, object_data['Description'])
        self.assertEqual(instance.duration, object_data['Duration'])
        self.assertEqual(instance.complete, object_data['Complete'])
        self.assertEqual(
            instance.create_date_time, object_data['CreateDateTime'])
        self.assertEqual(
            instance.start_date_time, object_data['StartDateTime'])
        self.assertEqual(instance.end_date_time, object_data['EndDateTime'])
        self.assertEqual(
            instance.canceled_date_time, object_data['CanceledDateTime'])
        self.assertEqual(
            instance.last_modified_date_time,
            object_data['LastModifiedDateTime']
        )
        self.assertEqual(instance.status.id, object_data['Status'])
        self.assertEqual(instance.account.id, object_data['AccountID'])
        self.assertEqual(
            instance.creator_resource.id, object_data['CreatorResourceID'])
        self.assertEqual(
            instance.canceled_by_resource.id,
            object_data['CanceledByResource']
        )

    def test_sync_service_call(self):
        """
        Test to ensure synchronizer saves a service call instance locally.
        """
        service_call = fixture_utils.generate_objects(
            'ServiceCall', fixtures.API_SERVICE_CALL_LIST
        )
        mocks.api_query_call(service_call)
        synchronizer = sync.ServiceCallSynchronizer()
        synchronizer.sync()

        self.assertGreater((ServiceCall.objects.count()), 0)

        object_data = fixtures.API_SERVICE_CALL
        instance = ServiceCall.objects.get(id=object_data['id'])

        self._assert_sync(instance, object_data)
        assert_sync_job(ServiceCall)

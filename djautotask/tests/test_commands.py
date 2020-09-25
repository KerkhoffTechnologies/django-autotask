import io
from atws.wrapper import Wrapper
from django.core.management import call_command
from django.test import TestCase
from djautotask.tests import fixtures, mocks, fixture_utils
from djautotask import models


def sync_summary(class_name, created_count, updated_count=0):
    return '{} Sync Summary - Created: {}, Updated: {}, Skipped: 0'.format(
        class_name, created_count, updated_count
    )


def full_sync_summary(class_name, deleted_count, updated_count=0):
    return '{} Sync Summary - Created: 0, Updated: {}, Skipped: 0, ' \
        'Deleted: {}'.format(class_name, updated_count, deleted_count)


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

    def get_api_mock(self):
        return mocks.api_query_call

    def get_return_value(self, at_object, fixture_list):
        return fixture_utils.generate_objects(
            at_object.title().replace('_', ''), fixture_list)

    def init_sync_command(self, fixture_list, at_object, full_option=False):
        return_value = self.get_return_value(at_object, fixture_list)
        api_call = self.get_api_mock()
        api_call(return_value)

        output = run_sync_command(full_option, at_object)
        return output

    def _test_sync(self):
        out = self.init_sync_command(*self.args)
        obj_title = self._title_for_at_object(self.args[-1])

        self.assertIn(obj_title, out.getvalue().strip())

    def test_full_sync(self):
        out = self.init_sync_command(*self.args)

        fixture_list, at_object = self.args
        args = [
            [],
            at_object,
        ]

        out = self.init_sync_command(*args, full_option=True)

        obj_label = self._title_for_at_object(at_object)
        msg_tmpl = '{} Sync Summary - Created: 0, Updated: 0, Skipped: 0, ' \
                   'Deleted: {}'

        value_count = len(fixture_list)

        msg = msg_tmpl.format(obj_label, value_count)

        self.assertEqual(msg, out.getvalue().strip())


class AbstractPicklistSyncCommandTest(AbstractBaseSyncTest):

    def get_return_value(self, at_object, fixture_list):
        field_info = fixture_utils.generate_picklist_objects(
            self.field_name, fixture_list)

        return field_info

    def get_api_mock(self):
        return mocks.api_picklist_call


class TestSyncTicketCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_TICKET_LIST,
        'ticket',
    )

    def setUp(self):
        super().setUp()
        # We can't test if query conditions actualy return the correct objects
        # so mock any Synchronizers with custom query conditions.
        mocks.create_mock_call(
            'djautotask.sync.TicketSynchronizer._get_query_conditions', None)
        fixture_utils.init_statuses()


class TestSyncStatusCommand(AbstractPicklistSyncCommandTest, TestCase):
    field_name = 'Status'

    args = (
        fixtures.API_STATUS_LIST,
        'status',
    )


class TestSyncPriorityCommand(AbstractPicklistSyncCommandTest, TestCase):
    field_name = 'Priority'

    args = (
        fixtures.API_PRIORITY_LIST,
        'priority',
    )


class TestSyncQueueCommand(AbstractPicklistSyncCommandTest, TestCase):
    field_name = 'QueueID'

    args = (
        fixtures.API_QUEUE_LIST,
        'queue',

    )


class TestSyncProjectStatusCommand(AbstractPicklistSyncCommandTest, TestCase):
    field_name = 'Status'

    args = (
        fixtures.API_PROJECT_STATUS_LIST,
        'project_status',
    )


class TestSyncProjectTypeCommand(AbstractPicklistSyncCommandTest, TestCase):
    field_name = 'Type'

    args = (
        fixtures.API_PROJECT_TYPE_LIST,
        'project_type',
    )


class TestSyncSourceCommand(AbstractPicklistSyncCommandTest, TestCase):
    field_name = 'Source'

    args = (
        fixtures.API_SOURCE_LIST,
        'source',
    )


class TestSyncIssueTypeCommand(AbstractPicklistSyncCommandTest, TestCase):
    field_name = 'IssueType'

    args = (
        fixtures.API_ISSUE_TYPE_LIST,
        'issue_type',
    )


class TestSyncSubIssueTypeCommand(AbstractPicklistSyncCommandTest, TestCase):
    field_name = 'SubIssueType'

    args = (
        fixtures.API_SUB_ISSUE_TYPE_LIST,
        'sub_issue_type',
    )


class TestSyncTicketTypeCommand(AbstractPicklistSyncCommandTest, TestCase):
    field_name = 'TicketType'

    args = (
        fixtures.API_TICKET_TYPE_LIST,
        'ticket_type',
    )


class TestSyncAccountTypeCommand(AbstractPicklistSyncCommandTest, TestCase):
    field_name = 'AccountType'

    args = (
        fixtures.API_ACCOUNT_TYPE_LIST,
        'account_type',
    )


class TestSyncServiceCallStatusCommand(AbstractPicklistSyncCommandTest,
                                       TestCase):
    field_name = 'Status'

    args = (
        fixtures.API_SERVICE_CALL_STATUS_LIST,
        'service_call_status',
    )


class TestDisplayColorCommand(AbstractPicklistSyncCommandTest, TestCase):
    field_name = 'DisplayColorRGB'

    args = (
        fixtures.API_DISPLAY_COLOR_LIST,
        'display_color',
    )


class TestLicenseTypeCommand(AbstractPicklistSyncCommandTest, TestCase):
    field_name = 'LicenseType'

    args = (
        fixtures.API_LICENSE_TYPE_LIST,
        'license_type',
    )


class TestSyncTaskTypeLinkCommand(AbstractPicklistSyncCommandTest, TestCase):
    field_name = 'Type'

    args = (
        fixtures.API_TASK_TYPE_LINK_LIST,
        'task_type_link',
    )


class TestUseTypeCommand(AbstractPicklistSyncCommandTest, TestCase):
    field_name = 'UseType'

    args = (
        fixtures.API_USE_TYPE_LIST,
        'use_type',
    )


class TestSyncTicketCategoryCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_TICKET_CATEGORY_LIST,
        'ticket_category',
    )


class TestSyncResourceCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_RESOURCE_LIST,
        'resource',
    )


class TestSyncTicketSecondaryResourceCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_SECONDARY_RESOURCE_LIST,
        'ticket_secondary_resource',
    )


class TestSyncAccountCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_ACCOUNT_LIST,
        'account',
    )


class TestSyncAccountLocationCommand(AbstractBaseSyncTest, TestCase):
    def setUp(self):
        super().setUp()
        fixture_utils.init_accounts()

    args = (
        fixtures.API_ACCOUNT_PHYSICAL_LOCATION_LIST,
        'account_physical_location',
    )


class TestSyncProjectCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_PROJECT_LIST,
        'project',
    )


class TestSyncPhaseCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_PHASE_LIST,
        'phase',
    )


class TestSyncTaskCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_TASK_LIST,
        'task',
    )

    def setUp(self):
        super().setUp()
        mocks.create_mock_call(
            'djautotask.sync.TaskSynchronizer._get_query_conditions', None)


class TestSyncTaskSecondaryResourceCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_TASK_SECONDARY_RESOURCE_LIST,
        'task_secondary_resource',
    )


class TestSyncTicketNoteCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_TICKET_NOTE_LIST,
        'ticket_note',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_tickets()
        fixture_utils.init_ticket_notes()


class TestSyncTaskNoteCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_TASK_NOTE_LIST,
        'task_note',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_tasks()
        fixture_utils.init_task_notes()


class TestSyncTimeEntryCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_TIME_ENTRY_LIST,
        'time_entry',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_tickets()


class TestAllocationCodeCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_ALLOCATION_CODE_LIST,
        'allocation_code',
    )


class TestSyncRoleCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_ROLE_LIST,
        'role',
    )


class TestSyncDepartmentCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_DEPARTMENT_LIST,
        'department',
    )


class TestResourceRoleDepartmentCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_RESOURCE_ROLE_DEPARTMENT_LIST,
        'resource_role_department',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_departments()
        fixture_utils.init_roles()
        fixture_utils.init_resources()


class TestResourceServiceDeskRoleCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_RESOURCE_SERVICE_DESK_ROLE_LIST,
        'resource_service_desk_role',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_roles()
        fixture_utils.init_resources()


class TestContractCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_CONTRACT_LIST,
        'contract',
    )


class TestSyncServiceCallCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_SERVICE_CALL_LIST,
        'service_call',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_service_call_statuses()
        fixture_utils.init_resources()
        fixture_utils.init_account_types()
        fixture_utils.init_accounts()


class TestSyncServiceCallTicketCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_SERVICE_CALL_TICKET_LIST,
        'service_call_ticket',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_service_call_statuses()
        fixture_utils.init_resources()
        fixture_utils.init_account_types()
        fixture_utils.init_accounts()
        fixture_utils.init_service_calls()
        fixture_utils.init_statuses()
        fixture_utils.init_tickets()


class TestSyncServiceCallTaskCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_SERVICE_CALL_TASK_LIST,
        'service_call_task',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_service_call_statuses()
        fixture_utils.init_account_types()
        fixture_utils.init_accounts()
        fixture_utils.init_service_calls()
        fixture_utils.init_statuses()
        fixture_utils.init_tasks()


class TestSyncServiceCallTicketResourceCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_SERVICE_CALL_TICKET_RESOURCE_LIST,
        'service_call_ticket_resource',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_service_call_statuses()
        fixture_utils.init_resources()
        fixture_utils.init_account_types()
        fixture_utils.init_accounts()
        fixture_utils.init_service_calls()
        fixture_utils.init_statuses()
        fixture_utils.init_tickets()
        fixture_utils.init_service_call_tickets()


class TestSyncServiceCallTaskResourceCommand(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_SERVICE_CALL_TASK_RESOURCE_LIST,
        'service_call_task_resource',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_service_call_statuses()
        fixture_utils.init_resources()
        fixture_utils.init_account_types()
        fixture_utils.init_accounts()
        fixture_utils.init_service_calls()
        fixture_utils.init_statuses()
        fixture_utils.init_tasks()
        fixture_utils.init_service_call_tasks()


class TestSyncTaskPredecessor(AbstractBaseSyncTest, TestCase):
    args = (
        fixtures.API_TASK_PREDECESSOR_LIST,
        'task_predecessor',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_tasks()


class TestSyncAllCommand(TestCase):

    def setUp(self):
        super().setUp()
        mocks.init_api_connection(Wrapper)
        mocks.create_mock_call(
            'djautotask.sync.TaskSynchronizer._get_query_conditions', None)
        mocks.create_mock_call(
            'djautotask.sync.TicketNoteSynchronizer._get_query_conditions',
            None
        )
        mocks.create_mock_call(
            'djautotask.sync.TaskNoteSynchronizer._get_query_conditions',
            None
        )
        mocks.create_mock_call(
            'djautotask.sync.QueryConditionMixin._get_query_conditions', None)

        # Mock API calls to return values based on what entity
        # is being requested
        mocks.get_field_info_api_calls(
            fixture_utils.manage_sync_picklist_return_data
        )
        mocks.wrapper_query_api_calls(
            fixture_utils.manage_full_sync_return_data
        )

        sync_test_cases = [
            TestSyncTicketCommand,
            TestSyncTaskCommand,
            TestSyncStatusCommand,
            TestSyncResourceCommand,
            TestSyncPriorityCommand,
            TestSyncQueueCommand,
            TestSyncAccountCommand,
            TestSyncProjectCommand,
            TestSyncProjectStatusCommand,
            TestSyncProjectTypeCommand,
            TestSyncTicketCategoryCommand,
            TestSyncSourceCommand,
            TestSyncIssueTypeCommand,
            TestSyncSubIssueTypeCommand,
            TestSyncTicketTypeCommand,
            TestDisplayColorCommand,
            TestLicenseTypeCommand,
            TestSyncTaskSecondaryResourceCommand,
            TestSyncPhaseCommand,
            TestSyncTicketNoteCommand,
            TestSyncTaskNoteCommand,
            TestSyncTimeEntryCommand,
            TestSyncTaskTypeLinkCommand,
            TestUseTypeCommand,
            TestAllocationCodeCommand,
            TestSyncRoleCommand,
            TestSyncDepartmentCommand,
            TestResourceRoleDepartmentCommand,
            TestResourceServiceDeskRoleCommand,
            TestContractCommand,
            TestSyncServiceCallStatusCommand,
            TestSyncServiceCallCommand,
            TestSyncServiceCallTicketCommand,
            TestSyncServiceCallTaskCommand,
            TestSyncServiceCallTicketResourceCommand,
            TestSyncServiceCallTaskResourceCommand,
            TestSyncAccountLocationCommand,
            TestSyncTaskPredecessor,
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

        for fixture, at_object in self.test_args:
            summary = sync_summary(slug_to_title(at_object), len(fixture))
            self.assertIn(summary, output.getvalue().strip())

        self.assertEqual(
            models.Ticket.objects.all().count(), len(fixtures.API_TICKET_LIST)
        )

    def test_full_sync(self):
        """Test the command to run a full sync of all objects."""
        at_object_map = {
            'status': models.Status,
            'ticket': models.Ticket,
            'resource': models.Resource,
            'ticket_secondary_resource': models.TicketSecondaryResource,
            'priority': models.Priority,
            'queue': models.Queue,
            'account': models.Account,
            'account_physical_location': models.AccountPhysicalLocation,
            'project': models.Project,
            'project_status': models.ProjectStatus,
            'project_type': models.ProjectType,
            'ticket_category': models.TicketCategory,
            'source': models.Source,
            'issue_type': models.IssueType,
            'sub_issue_type': models.SubIssueType,
            'ticket_type': models.TicketType,
            'display_color': models.DisplayColor,
            'license_type': models.LicenseType,
            'task': models.Task,
            'task_secondary_resource': models.TaskSecondaryResource,
            'phase': models.Phase,
            'ticket_note': models.TicketNote,
            'task_note': models.TaskNote,
            'time_entry': models.TimeEntry,
            'task_type_link': models.TaskTypeLink,
            'use_type': models.UseType,
            'allocation_code': models.AllocationCode,
            'role': models.Role,
            'department': models.Department,
            'resource_role_department': models.ResourceRoleDepartment,
            'resource_service_desk_role': models.ResourceServiceDeskRole,
            'contract': models.Contract,
            'service_call_status': models.ServiceCallStatus,
            'service_call': models.ServiceCall,
            'service_call_ticket': models.ServiceCallTicket,
            'service_call_task': models.ServiceCallTask,
            'service_call_ticket_resource': models.ServiceCallTicketResource,
            'service_call_task_resource': models.ServiceCallTaskResource,
            'task_predecessor': models.TaskPredecessor,
        }
        run_sync_command()
        pre_full_sync_counts = {}

        mocks.wrapper_query_api_calls()
        mocks.get_field_info_api_calls()
        _, _patch = mocks.build_batch_query()

        for key, model_class in at_object_map.items():
            pre_full_sync_counts[key] = model_class.objects.all().count()

        output = run_sync_command(full_option=True)

        # Verify the rest of sync classes summaries.
        for fixture, at_object in self.test_args:
            if at_object in (
                    'resource_role_department',
                    'resource_service_desk_role',
                    'service_call',
                    'service_call_ticket',
                    'service_call_task',
                    'service_call_ticket_resource',
                    'service_call_task_resource',
                    'task_predecessor',
            ):
                # Assert that there were objects to get deleted, then change
                # to zero to verify the output formats correctly.
                # We are just testing the command, there are sync tests to
                # verify that the syncronizers work correctly
                self.assertGreater(pre_full_sync_counts[at_object], 0)
                pre_full_sync_counts[at_object] = 0
            summary = full_sync_summary(
                slug_to_title(at_object),
                pre_full_sync_counts[at_object]
            )
            self.assertIn(summary, output.getvalue().strip())

        _patch.stop()

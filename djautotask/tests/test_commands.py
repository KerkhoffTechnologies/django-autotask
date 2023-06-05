import io
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
        super().setUp()
        mocks.init_api_rest_connection()

    def _test_sync(self, mock_call, return_value, at_object,
                   full_option=False):
        mock_call(return_value)
        out = io.StringIO()

        args = ['atsync', at_object]
        if full_option:
            args.append('--full')
        call_command(*args, stdout=out)
        return out

    def _title_for_at_object(self, at_object):
        return at_object.title().replace('_', ' ')

    def test_sync(self):
        out = self._test_sync(*self.args)
        obj_title = self._title_for_at_object(self.args[-1])
        self.assertIn(obj_title, out.getvalue().strip())

    def test_full_sync(self):
        self.test_sync()
        mock_call, return_value, at_object = self.args
        args = [
            mock_call,
            {
                "items": [],
                "pageDetails": fixtures.API_PAGE_DETAILS
            },
            at_object
        ]

        out = self._test_sync(*args, full_option=True)
        obj_label = self._title_for_at_object(at_object)
        msg_tmpl = '{} Sync Summary - Created: 0, Updated: 0, Skipped: 0, ' \
                   'Deleted: {}'
        msg = msg_tmpl.format(obj_label, len(return_value.get('items')))
        self.assertEqual(msg, out.getvalue().strip())


class PicklistSyncTest(AbstractBaseSyncTest):

    def test_full_sync(self):
        self.test_sync()
        mock_call, return_value, at_object = self.args
        args = [
            mock_call,
            {
                "fields": []
            },
            at_object
        ]

        out = self._test_sync(*args, full_option=True)
        obj_label = self._title_for_at_object(at_object)
        msg_tmpl = '{} Sync Summary - Created: 0, Updated: 0, Skipped: 0, ' \
                   'Deleted: {}'
        msg = msg_tmpl.format(
            obj_label, len(return_value.get('fields')[0].get('picklistValues'))
        )
        self.assertEqual(msg, out.getvalue().strip())


class TestSyncTicketUDFCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_ticket_udf_call,
        fixtures.API_UDF,
        'ticket_udf',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_ticket_udfs()


class TestSyncTaskUDFCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_task_udf_call,
        fixtures.API_UDF,
        'task_udf',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_task_udfs()


class TestSyncProjectUDFCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_project_udf_call,
        fixtures.API_UDF,
        'project_udf',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_project_udfs()


class TestSyncContactCommand(AbstractBaseSyncTest, TestCase):
    args = (
        mocks.service_api_get_contacts_call,
        fixtures.API_CONTACT,
        'contact',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_contacts()


class TestSyncTicketCommand(AbstractBaseSyncTest, TestCase):
    args = (
        mocks.service_api_get_tickets_call,
        fixtures.API_TICKET,
        'ticket',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_tickets()


class TestSyncStatusCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_ticket_picklist_call,
        fixtures.API_STATUS_FIELD,
        'status',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_statuses()


class TestSyncPriorityCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_ticket_picklist_call,
        fixtures.API_PRIORITY_FIELD,
        'priority',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_priorities()


class TestSyncQueueCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_ticket_picklist_call,
        fixtures.API_QUEUE_FIELD,
        'queue',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_queues()


class TestSyncProjectStatusCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_project_picklist_call,
        fixtures.API_PROJECT_STATUS_FIELD,
        'project_status',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_project_statuses()


class TestSyncProjectTypeCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_project_picklist_call,
        fixtures.API_PROJECT_TYPE_FIELD,
        'project_type',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_project_types()


class TestSyncSourceCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_ticket_picklist_call,
        fixtures.API_SOURCE_FIELD,
        'source',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_sources()


class TestSyncIssueTypeCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_ticket_picklist_call,
        fixtures.API_ISSUE_TYPE_FIELD,
        'issue_type',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_issue_types()


class TestSyncSubIssueTypeCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_ticket_picklist_call,
        fixtures.API_SUB_ISSUE_TYPE_FIELD,
        'sub_issue_type',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_issue_types()
        fixture_utils.init_sub_issue_types()


class TestSyncTicketTypeCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_ticket_picklist_call,
        fixtures.API_TICKET_TYPE_FIELD,
        'ticket_type',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_ticket_types()


class TestSyncAccountTypeCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_account_types_call,
        fixtures.API_ACCOUNT_TYPE_FIELD,
        'account_type',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_account_types()


class TestSyncServiceCallStatusCommand(PicklistSyncTest,
                                       TestCase):
    args = (
        mocks.service_api_get_service_call_statuses_call,
        fixtures.API_SERVICE_CALL_STATUS_FIELD,
        'service_call_status',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_service_call_statuses()


class TestSyncDisplayColorCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_ticket_category_picklist_call,
        fixtures.API_DISPLAY_COLOR_FIELD,
        'display_color',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_display_colors()


class TestSyncNoteTypeCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_note_types_call,
        fixtures.API_NOTE_TYPE_FIELD,
        'note_type',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_note_types()


class TestProjectNoteTypeCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_project_note_types_call,
        fixtures.API_PROJECT_NOTE_TYPE_FIELD,
        'project_note_type',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_project_note_types()


class TestSyncLicenseTypeCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_license_types_call,
        fixtures.API_LICENSE_TYPE_FIELD,
        'license_type',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_license_types()


class TestSyncTaskTypeLinkCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_task_type_links_call,
        fixtures.API_TASK_TYPE_LINK_FIELD,
        'task_type_link',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_task_type_links()


class TestSyncTaskCategoryCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_task_picklist_call,
        fixtures.API_TASK_CATEGORY_FIELD,
        'task_category',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_task_categories()


class TestSyncUseTypeCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_use_types_call,
        fixtures.API_USE_TYPE_FIELD,
        'use_type',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_use_types()


class TestSyncBillingCodeTypeCommand(PicklistSyncTest, TestCase):
    args = (
        mocks.service_api_get_billing_code_types_call,
        fixtures.API_BILLING_CODE_TYPE_FIELD,
        'billing_code_type',
    )


class TestSyncTicketCategoryCommand(AbstractBaseSyncTest, TestCase):
    args = (
        mocks.service_api_get_ticket_categories_call,
        fixtures.API_TICKET_CATEGORY,
        'ticket_category',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_ticket_categories()


class TestSyncResourceCommand(AbstractBaseSyncTest, TestCase):
    args = (
        mocks.service_api_get_resources_call,
        fixtures.API_RESOURCE,
        'resource',
    )


class TestSyncAccountCommand(AbstractBaseSyncTest, TestCase):
    args = (
        mocks.service_api_get_accounts_call,
        fixtures.API_ACCOUNT,
        'account',
    )


class TestSyncAccountLocationCommand(AbstractBaseSyncTest, TestCase):
    args = (
        mocks.service_api_get_account_physical_locations_call,
        fixtures.API_ACCOUNT_PHYSICAL_LOCATION,
        'account_physical_location',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_accounts()
        fixture_utils.init_account_physical_locations()


class TestSyncProjectCommand(AbstractBaseSyncTest, TestCase):
    args = (
        mocks.service_api_get_projects_call,
        fixtures.API_PROJECT,
        'project',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_projects()


class TestSyncPhaseCommand(AbstractBaseSyncTest, TestCase):
    args = (
        mocks.service_api_get_phases_call,
        fixtures.API_PHASE,
        'phase',
    )


class TestSyncTaskCommand(AbstractBaseSyncTest, TestCase):
    args = (
        mocks.service_api_get_tasks_call,
        fixtures.API_TASK,
        'task',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_projects()
        fixture_utils.init_tasks()


class TestSyncTicketSecondaryResourceCommand(AbstractBaseSyncTest,
                                             TestCase):
    args = (
        mocks.service_api_get_ticket_secondary_resources_call,
        fixtures.API_TICKET_SECONDARY_RESOURCE,
        'ticket_secondary_resource',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_tickets()


class TestSyncTaskSecondaryResourceCommand(AbstractBaseSyncTest, TestCase):
    args = (
        mocks.service_api_get_task_secondary_resources_call,
        fixtures.API_TASK_SECONDARY_RESOURCE,
        'task_secondary_resource',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_projects()
        fixture_utils.init_tasks()


class TestSyncTicketNoteCommand(AbstractBaseSyncTest, TestCase):
    args = (
        mocks.service_api_get_ticket_notes_call,
        fixtures.API_TICKET_NOTE,
        'ticket_note',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_tickets()
        fixture_utils.init_ticket_notes()


class TestSyncTaskNoteCommand(AbstractBaseSyncTest, TestCase):
    args = (
        mocks.service_api_get_task_notes_call,
        fixtures.API_TASK_NOTE,
        'task_note',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_projects()
        fixture_utils.init_tasks()
        fixture_utils.init_task_notes()


class TestSyncTimeEntryCommand(AbstractBaseSyncTest, TestCase):
    args = (
        mocks.service_api_get_time_entries_call,
        fixtures.API_TIME_ENTRY,
        'time_entry',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_resources()
        fixture_utils.init_projects()
        fixture_utils.init_tasks()
        fixture_utils.init_tickets()
        fixture_utils.init_time_entries()


class TestSyncBillingCodeCommand(AbstractBaseSyncTest, TestCase):
    args = (
        mocks.service_api_get_billing_codes_call,
        fixtures.API_BILLING_CODE,
        'billing_code',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_billing_codes()


class TestSyncRoleCommand(AbstractBaseSyncTest, TestCase):
    args = (
        mocks.service_api_get_roles_call,
        fixtures.API_ROLE,
        'role',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_roles()


class TestSyncDepartmentCommand(AbstractBaseSyncTest, TestCase):
    args = (
        mocks.service_api_get_departments_call,
        fixtures.API_DEPARTMENT,
        'department',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_departments()


class TestSyncResourceServiceDeskRoleCommand(AbstractBaseSyncTest,
                                             TestCase):
    args = (
        mocks.service_api_get_resource_service_desk_roles_call,
        fixtures.API_RESOURCE_SERVICE_DESK_ROLE,
        'resource_service_desk_role',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_roles()
        fixture_utils.init_resources()
        fixture_utils.init_resource_service_desk_roles()


class TestSyncResourceRoleDepartmentCommand(AbstractBaseSyncTest,
                                            TestCase):
    args = (
        mocks.service_api_get_resource_role_departments_call,
        fixtures.API_RESOURCE_ROLE_DEPARTMENT,
        'resource_role_department',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_departments()
        fixture_utils.init_roles()
        fixture_utils.init_resources()
        fixture_utils.init_resource_role_departments()


class TestSyncContractCommand(AbstractBaseSyncTest, TestCase):
    args = (
        mocks.service_api_get_contracts_call,
        fixtures.API_CONTRACT,
        'contract',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_contracts()


class TestSyncServiceCallCommand(AbstractBaseSyncTest, TestCase):
    args = (
        mocks.service_api_get_service_calls_call,
        fixtures.API_SERVICE_CALL,
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
        mocks.service_api_get_service_call_tickets_call,
        fixtures.API_SERVICE_CALL_TICKET,
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
        mocks.service_api_get_service_call_tasks_call,
        fixtures.API_SERVICE_CALL_TASK,
        'service_call_task',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_service_call_statuses()
        fixture_utils.init_account_types()
        fixture_utils.init_accounts()
        fixture_utils.init_service_calls()
        fixture_utils.init_statuses()
        fixture_utils.init_projects()
        fixture_utils.init_tasks()


class TestSyncServiceCallTicketResourceCommand(AbstractBaseSyncTest,
                                               TestCase):
    args = (
        mocks.service_api_get_service_call_ticket_resources_call,
        fixtures.API_SERVICE_CALL_TICKET_RESOURCE,
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


class TestSyncServiceCallTaskResourceCommand(AbstractBaseSyncTest,
                                             TestCase):
    args = (
        mocks.service_api_get_service_call_task_resources_call,
        fixtures.API_SERVICE_CALL_TASK_RESOURCE,
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
        fixture_utils.init_projects()
        fixture_utils.init_tasks()
        fixture_utils.init_service_call_tasks()


class TestSyncTaskPredecessor(AbstractBaseSyncTest, TestCase):
    args = (
        mocks.service_api_get_task_predecessors_call,
        fixtures.API_TASK_PREDECESSOR,
        'task_predecessor',
    )

    def setUp(self):
        super().setUp()
        fixture_utils.init_projects()
        fixture_utils.init_tasks()
        fixture_utils.init_task_predecessors()


class TestSyncAllCommand(TestCase):

    def setUp(self):
        super().setUp()
        mocks.init_api_rest_connection()
        self._call_service_api()

        sync_test_cases = [
            TestSyncTicketUDFCommand,
            TestSyncTaskUDFCommand,
            TestSyncProjectUDFCommand,
            TestSyncNoteTypeCommand,
            TestProjectNoteTypeCommand,
            TestSyncLicenseTypeCommand,
            TestSyncTaskTypeLinkCommand,
            TestSyncUseTypeCommand,
            TestSyncBillingCodeTypeCommand,
            TestSyncAccountTypeCommand,
            TestSyncRoleCommand,
            TestSyncDepartmentCommand,
            TestSyncTicketCommand,
            TestSyncTaskCategoryCommand,
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
            TestSyncDisplayColorCommand,
            TestSyncTaskSecondaryResourceCommand,
            TestSyncPhaseCommand,
            TestSyncTicketNoteCommand,
            TestSyncTaskNoteCommand,
            TestSyncTimeEntryCommand,
            TestSyncBillingCodeCommand,
            TestSyncResourceRoleDepartmentCommand,
            TestSyncResourceServiceDeskRoleCommand,
            TestSyncContractCommand,
            TestSyncServiceCallStatusCommand,
            TestSyncServiceCallCommand,
            TestSyncServiceCallTicketCommand,
            TestSyncServiceCallTaskCommand,
            TestSyncServiceCallTicketResourceCommand,
            TestSyncServiceCallTaskResourceCommand,
            TestSyncAccountLocationCommand,
            TestSyncTaskPredecessor,
            TestSyncContactCommand,
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

        for mock_call, fixture, at_object in self.test_args:
            if mock_call:
                if 'fields' in fixture:
                    fixture_len = \
                        len(fixture.get('fields')[0].get('picklistValues'))
                else:
                    fixture_len = len(fixture.get('items'))
            else:
                fixture_len = len(fixture)
            summary = sync_summary(slug_to_title(at_object), fixture_len)
            self.assertIn(summary, output.getvalue().strip())

        self.assertEqual(
            models.Ticket.objects.all().count(),
            len(fixtures.API_TICKET['items'])
        )

    def test_full_sync(self):
        """Test the command to run a full sync of all objects."""
        at_object_map = {
            'ticket_udf': models.TicketUDF,
            'task_udf': models.TaskUDF,
            'project_udf': models.ProjectUDF,
            'note_type': models.NoteType,
            'account_type': models.AccountType,
            'role': models.Role,
            'department': models.Department,
            'status': models.Status,
            'priority': models.Priority,
            'queue': models.Queue,
            'source': models.Source,
            'issue_type': models.IssueType,
            'display_color': models.DisplayColor,
            'ticket': models.Ticket,
            'resource': models.Resource,
            'ticket_secondary_resource': models.TicketSecondaryResource,
            'account': models.Account,
            'account_physical_location': models.AccountPhysicalLocation,
            'project': models.Project,
            'project_status': models.ProjectStatus,
            'project_type': models.ProjectType,
            'project_note_type': models.ProjectNoteType,
            'ticket_category': models.TicketCategory,
            'sub_issue_type': models.SubIssueType,
            'ticket_type': models.TicketType,
            'license_type': models.LicenseType,
            'task_category': models.TaskCategory,
            'task': models.Task,
            'task_secondary_resource': models.TaskSecondaryResource,
            'phase': models.Phase,
            'ticket_note': models.TicketNote,
            'task_note': models.TaskNote,
            'time_entry': models.TimeEntry,
            'task_type_link': models.TaskTypeLink,
            'use_type': models.UseType,
            'billing_code_type': models.BillingCodeType,
            'billing_code': models.BillingCode,
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
            'contact': models.Contact,
        }
        run_sync_command()
        pre_full_sync_counts = {}

        self._call_empty_service_api()
        for key, model_class in at_object_map.items():
            pre_full_sync_counts[key] = model_class.objects.all().count()

        output = run_sync_command(full_option=True)

        # Verify the rest of sync classes summaries.
        for mock_call, fixture, at_object in self.test_args:
            if at_object in (
                    'resource_role_department',
                    'resource_service_desk_role',
                    'service_call',
                    'service_call_ticket',
                    'service_call_task',
                    'service_call_ticket_resource',
                    'service_call_task_resource',
                    'task_predecessor',
                    'task',
                    'time_entry'
            ):
                # Assert that there were objects to get deleted, then change
                # to zero to verify the output formats correctly.
                # We are just testing the command, there are sync tests to
                # verify that the synchronizers work correctly
                self.assertGreater(pre_full_sync_counts[at_object], 0)
                pre_full_sync_counts[at_object] = 0
            summary = full_sync_summary(
                slug_to_title(at_object),
                pre_full_sync_counts[at_object]
            )
            self.assertIn(summary, output.getvalue().strip())

    def _call_service_api(self):
        mocks.service_api_get_ticket_udf_call(fixtures.API_UDF)
        mocks.service_api_get_task_udf_call(fixtures.API_UDF)
        mocks.service_api_get_project_udf_call(fixtures.API_UDF)
        mocks.service_api_get_roles_call(fixtures.API_ROLE)
        mocks.service_api_get_departments_call(fixtures.API_DEPARTMENT)
        mocks.service_api_get_resource_service_desk_roles_call(
            fixtures.API_RESOURCE_SERVICE_DESK_ROLE)
        mocks.service_api_get_resource_role_departments_call(
            fixtures.API_RESOURCE_ROLE_DEPARTMENT)
        mocks.service_api_get_license_types_call(
            fixtures.API_LICENSE_TYPE_FIELD)
        mocks.service_api_get_use_types_call(fixtures.API_USE_TYPE_FIELD)
        mocks.service_api_get_billing_code_types_call(
            fixtures.API_BILLING_CODE_TYPE_FIELD)
        mocks.service_api_get_task_type_links_call(
            fixtures.API_TASK_TYPE_LINK_FIELD)
        mocks.service_api_get_account_types_call(
            fixtures.API_ACCOUNT_TYPE_FIELD)
        mocks.service_api_get_ticket_category_picklist_call(
            fixtures.API_DISPLAY_COLOR_FIELD)
        mocks.service_api_get_ticket_picklist_call(
            fixtures.API_TICKET_PICKLIST_FIELD)
        mocks.service_api_get_project_picklist_call(
            fixtures.API_PROJECT_PICKLIST_FIELD)
        mocks.service_api_get_service_call_statuses_call(
            fixtures.API_SERVICE_CALL_STATUS_FIELD)
        mocks.service_api_get_note_types_call(fixtures.API_NOTE_TYPE_FIELD)
        mocks.service_api_get_project_note_types_call(
            fixtures.API_PROJECT_NOTE_TYPE_FIELD)
        mocks.service_api_get_task_picklist_call(
            fixtures.API_TASK_CATEGORY_FIELD)

        mocks.service_api_get_contacts_call(fixtures.API_CONTACT)
        mocks.service_api_get_contracts_call(fixtures.API_CONTRACT)
        mocks.service_api_get_billing_codes_call(
            fixtures.API_BILLING_CODE)
        mocks.service_api_get_account_physical_locations_call(
            fixtures.API_ACCOUNT_PHYSICAL_LOCATION)
        mocks.service_api_get_ticket_categories_call(
            fixtures.API_TICKET_CATEGORY)
        mocks.service_api_get_tickets_call(fixtures.API_TICKET)
        mocks.service_api_get_tasks_call(fixtures.API_TASK)
        mocks.service_api_get_projects_call(fixtures.API_PROJECT)
        mocks.service_api_get_service_calls_call(fixtures.API_SERVICE_CALL)
        mocks.service_api_get_service_call_tickets_call(
            fixtures.API_SERVICE_CALL_TICKET)
        mocks.service_api_get_resources_call(fixtures.API_RESOURCE)
        mocks.service_api_get_accounts_call(fixtures.API_ACCOUNT)
        mocks.service_api_get_phases_call(fixtures.API_PHASE)
        mocks.service_api_get_service_call_ticket_resources_call(
            fixtures.API_SERVICE_CALL_TICKET_RESOURCE)
        mocks.service_api_get_service_call_tasks_call(
            fixtures.API_SERVICE_CALL_TASK)
        mocks.service_api_get_ticket_secondary_resources_call(
            fixtures.API_TICKET_SECONDARY_RESOURCE)
        mocks.service_api_get_task_secondary_resources_call(
            fixtures.API_TASK_SECONDARY_RESOURCE)
        mocks.service_api_get_ticket_notes_call(fixtures.API_TICKET_NOTE)
        mocks.service_api_get_task_notes_call(fixtures.API_TASK_NOTE)
        mocks.service_api_get_time_entries_call(fixtures.API_TIME_ENTRY)
        mocks.service_api_get_service_call_task_resources_call(
            fixtures.API_SERVICE_CALL_TASK_RESOURCE)
        mocks.service_api_get_task_predecessors_call(
            fixtures.API_TASK_PREDECESSOR)

    def _call_empty_service_api(self):
        mocks.service_api_get_ticket_udf_call(fixtures.API_EMPTY_FIELDS)
        mocks.service_api_get_task_udf_call(fixtures.API_EMPTY_FIELDS)
        mocks.service_api_get_project_udf_call(fixtures.API_EMPTY_FIELDS)
        mocks.service_api_get_contacts_call(fixtures.API_EMPTY)
        mocks.service_api_get_contracts_call(fixtures.API_EMPTY)
        mocks.service_api_get_billing_codes_call(fixtures.API_EMPTY)
        mocks.service_api_get_account_physical_locations_call(
            fixtures.API_EMPTY)
        mocks.service_api_get_tickets_call(fixtures.API_EMPTY)
        mocks.service_api_get_tasks_call(fixtures.API_EMPTY)
        mocks.service_api_get_projects_call(fixtures.API_EMPTY)
        mocks.service_api_get_ticket_categories_call(fixtures.API_EMPTY)
        mocks.service_api_get_task_predecessors_call(fixtures.API_EMPTY)
        mocks.service_api_get_roles_call(fixtures.API_EMPTY)
        mocks.service_api_get_departments_call(fixtures.API_EMPTY)
        mocks.service_api_get_resource_service_desk_roles_call(
            fixtures.API_EMPTY)
        mocks.service_api_get_resource_role_departments_call(
            fixtures.API_EMPTY)
        mocks.service_api_get_service_calls_call(fixtures.API_EMPTY)
        mocks.service_api_get_service_call_tickets_call(fixtures.API_EMPTY)
        mocks.service_api_get_resources_call(fixtures.API_EMPTY)
        mocks.service_api_get_accounts_call(fixtures.API_EMPTY)
        mocks.service_api_get_phases_call(fixtures.API_EMPTY)
        mocks.service_api_get_service_call_ticket_resources_call(
            fixtures.API_EMPTY)
        mocks.service_api_get_service_call_tasks_call(fixtures.API_EMPTY)
        mocks.service_api_get_ticket_secondary_resources_call(
            fixtures.API_EMPTY)
        mocks.service_api_get_task_secondary_resources_call(
            fixtures.API_EMPTY)
        mocks.service_api_get_ticket_notes_call(fixtures.API_EMPTY)
        mocks.service_api_get_task_notes_call(fixtures.API_EMPTY)
        mocks.service_api_get_time_entries_call(fixtures.API_EMPTY)
        mocks.service_api_get_service_call_task_resources_call(
            fixtures.API_EMPTY)
        mocks.service_api_get_ticket_category_picklist_call(
            fixtures.API_EMPTY_FIELDS)
        mocks.service_api_get_ticket_picklist_call(fixtures.API_EMPTY_FIELDS)
        mocks.service_api_get_project_picklist_call(fixtures.API_EMPTY_FIELDS)
        mocks.service_api_get_license_types_call(fixtures.API_EMPTY_FIELDS)
        mocks.service_api_get_use_types_call(fixtures.API_EMPTY_FIELDS)
        mocks.service_api_get_billing_code_types_call(
            fixtures.API_EMPTY_FIELDS)
        mocks.service_api_get_task_type_links_call(fixtures.API_EMPTY_FIELDS)
        mocks.service_api_get_account_types_call(fixtures.API_EMPTY_FIELDS)
        mocks.service_api_get_service_call_statuses_call(
            fixtures.API_EMPTY_FIELDS)
        mocks.service_api_get_note_types_call(fixtures.API_EMPTY_FIELDS)
        mocks.service_api_get_project_note_types_call(
            fixtures.API_EMPTY_FIELDS)
        mocks.service_api_get_task_picklist_call(fixtures.API_EMPTY_FIELDS)

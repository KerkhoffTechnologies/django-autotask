from mock import patch
import json
import responses


def create_mock_call(method_name, return_value, side_effect=None):
    """Utility function for mocking the specified function or method"""
    _patch = patch(method_name, side_effect=side_effect)
    mock_get_call = _patch.start()

    if not side_effect:
        mock_get_call.return_value = return_value

    return mock_get_call, _patch


def init_api_rest_connection(return_value=None):
    method_name = 'djautotask.api.get_api_connection_url'
    return create_mock_call(method_name, return_value)


def init_zone_info_connection(return_value=None):
    method_name = 'djautotask.api.get_zone_info'
    return create_mock_call(method_name, return_value)


def service_api_get_ticket_udf_call(return_value):
    method_name = 'djautotask.api.TicketsUDFAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_task_udf_call(return_value):
    method_name = 'djautotask.api.TasksUDFAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_project_udf_call(return_value):
    method_name = 'djautotask.api.ProjectsUDFAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_ticket_call(return_value):
    method_name = 'djautotask.api.TicketsAPIClient.get_single'
    return create_mock_call(method_name, return_value)


def service_api_get_contacts_call(return_value):
    method_name = 'djautotask.api.ContactsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_contracts_call(return_value):
    method_name = 'djautotask.api.ContractsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_billing_codes_call(return_value):
    method_name = 'djautotask.api.BillingCodesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_account_physical_locations_call(return_value):
    method_name = 'djautotask.api.AccountPhysicalLocationsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_accounts_call(return_value):
    method_name = 'djautotask.api.AccountsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_roles_call(return_value):
    method_name = 'djautotask.api.RolesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_departments_call(return_value):
    method_name = 'djautotask.api.DepartmentsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_resources_call(return_value):
    method_name = 'djautotask.api.ResourcesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_phases_call(return_value):
    method_name = 'djautotask.api.PhasesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_note_types_call(return_value):
    method_name = 'djautotask.api.NoteTypesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_project_note_types_call(return_value):
    method_name = 'djautotask.api.ProjectNoteTypesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_resource_service_desk_roles_call(return_value):
    method_name = 'djautotask.api.ResourceServiceDeskRolesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_resource_role_departments_call(return_value):
    method_name = 'djautotask.api.ResourceRoleDepartmentsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_tickets_call(return_value):
    method_name = 'djautotask.api.TicketsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_tasks_call(return_value):
    method_name = 'djautotask.api.TasksAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_projects_call(return_value):
    method_name = 'djautotask.api.ProjectsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_ticket_categories_call(return_value):
    method_name = 'djautotask.api.TicketCategoriesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_ticket_secondary_resources_call(return_value):
    method_name = 'djautotask.api.TicketSecondaryResourcesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_task_secondary_resources_call(return_value):
    method_name = 'djautotask.api.TaskSecondaryResourcesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_ticket_notes_call(return_value):
    method_name = 'djautotask.api.TicketNotesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_task_notes_call(return_value):
    method_name = 'djautotask.api.TaskNotesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_time_entries_call(return_value):
    method_name = 'djautotask.api.TimeEntriesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_task_predecessors_call(return_value):
    method_name = 'djautotask.api.TaskPredecessorsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_ticket_category_picklist_call(return_value):
    method_name = 'djautotask.api.TicketCategoryPicklistAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_ticket_picklist_call(return_value):
    method_name = 'djautotask.api.TicketPicklistAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_task_picklist_call(return_value):
    method_name = 'djautotask.api.TaskPicklistAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_project_picklist_call(return_value):
    method_name = 'djautotask.api.ProjectPicklistAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_license_types_call(return_value):
    method_name = 'djautotask.api.LicenseTypesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_service_call_statuses_call(return_value):
    method_name = 'djautotask.api.ServiceCallStatusPicklistAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_service_calls_call(return_value):
    method_name = 'djautotask.api.ServiceCallsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_service_call_tickets_call(return_value):
    method_name = 'djautotask.api.ServiceCallTicketsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_service_call_ticket_resources_call(return_value):
    method_name = 'djautotask.api.ServiceCallTicketResourcesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_service_call_tasks_call(return_value):
    method_name = 'djautotask.api.ServiceCallTasksAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_service_call_task_resources_call(return_value):
    method_name = 'djautotask.api.ServiceCallTaskResourcesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_use_types_call(return_value):
    method_name = 'djautotask.api.UseTypesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_billing_code_types_call(return_value):
    method_name = 'djautotask.api.BillingCodeTypeAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_task_type_links_call(return_value):
    method_name = \
        'djautotask.api.TaskTypeLinksAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_account_types_call(return_value):
    method_name = 'djautotask.api.AccountTypesAPIClient.get'
    return create_mock_call(method_name, return_value)


def get(url, data, headers=None, status=200):
    """Set up requests mock for given URL and JSON-serializable data."""
    get_raw(url, json.dumps(data), "application/json", headers, status=status)


def get_raw(url, data, content_type="application/octet-stream", headers=None,
            status=200):
    """Set up requests mock for given URL."""
    responses.add(
        responses.GET,
        url,
        body=data,
        status=status,
        content_type=content_type,
        adding_headers=headers,
    )

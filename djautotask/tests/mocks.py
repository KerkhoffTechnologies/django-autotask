from mock import patch
import json
import responses
from django.core.cache import cache


def create_mock_call(method_name, return_value, side_effect=None):
    """Utility function for mocking the specified function or method"""
    _patch = patch(method_name, side_effect=side_effect)
    mock_get_call = _patch.start()

    if not side_effect:
        mock_get_call.return_value = return_value

    return mock_get_call, _patch


def init_api_rest_connection(return_value=None):
    method_name = 'djautotask.api_rest.get_api_connection_url'
    cache.set('zone_info_url', return_value)
    return create_mock_call(method_name, return_value)


def service_api_get_ticket_call(return_value):
    method_name = 'djautotask.api_rest.TicketsAPIClient.get_single'
    return create_mock_call(method_name, return_value)


def service_api_get_contacts_call(return_value):
    method_name = 'djautotask.api_rest.ContactsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_contracts_call(return_value):
    method_name = 'djautotask.api_rest.ContractsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_allocation_codes_call(return_value):
    method_name = 'djautotask.api_rest.AllocationCodesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_account_physical_locations_call(return_value):
    method_name = 'djautotask.api_rest.AccountPhysicalLocationsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_accounts_call(return_value):
    method_name = 'djautotask.api_rest.AccountsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_roles_call(return_value):
    method_name = 'djautotask.api_rest.RolesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_departments_call(return_value):
    method_name = 'djautotask.api_rest.DepartmentsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_resources_call(return_value):
    method_name = 'djautotask.api_rest.ResourcesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_phases_call(return_value):
    method_name = 'djautotask.api_rest.PhasesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_note_types_call(return_value):
    method_name = 'djautotask.api_rest.NoteTypesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_resource_service_desk_roles_call(return_value):
    method_name = 'djautotask.api_rest.ResourceServiceDeskRolesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_resource_role_departments_call(return_value):
    method_name = 'djautotask.api_rest.ResourceRoleDepartmentsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_tickets_call(return_value):
    method_name = 'djautotask.api_rest.TicketsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_tasks_call(return_value):
    method_name = 'djautotask.api_rest.TasksAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_projects_call(return_value):
    method_name = 'djautotask.api_rest.ProjectsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_ticket_categories_call(return_value):
    method_name = 'djautotask.api_rest.TicketCategoriesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_ticket_secondary_resources_call(return_value):
    method_name = 'djautotask.api_rest.TicketSecondaryResourcesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_task_secondary_resources_call(return_value):
    method_name = 'djautotask.api_rest.TaskSecondaryResourcesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_ticket_notes_call(return_value):
    method_name = 'djautotask.api_rest.TicketNotesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_task_notes_call(return_value):
    method_name = 'djautotask.api_rest.TaskNotesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_time_entries_call(return_value):
    method_name = 'djautotask.api_rest.TimeEntriesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_task_predecessors_call(return_value):
    method_name = 'djautotask.api_rest.TaskPredecessorsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_ticket_category_picklist_call(return_value):
    method_name = 'djautotask.api_rest.TicketCategoryPicklistAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_ticket_picklist_call(return_value):
    method_name = 'djautotask.api_rest.TicketPicklistAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_project_picklist_call(return_value):
    method_name = 'djautotask.api_rest.ProjectPicklistAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_license_types_call(return_value):
    method_name = 'djautotask.api_rest.LicenseTypesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_service_call_statuses_call(return_value):
    method_name = 'djautotask.api_rest.ServiceCallStatusPicklistAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_service_calls_call(return_value):
    method_name = 'djautotask.api_rest.ServiceCallsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_service_call_tickets_call(return_value):
    method_name = 'djautotask.api_rest.ServiceCallTicketsAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_service_call_ticket_resources_call(return_value):
    method_name = 'djautotask.api_rest.ServiceCallTicketResourcesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_service_call_tasks_call(return_value):
    method_name = 'djautotask.api_rest.ServiceCallTasksAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_service_call_task_resources_call(return_value):
    method_name = 'djautotask.api_rest.ServiceCallTaskResourcesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_use_types_call(return_value):
    method_name = 'djautotask.api_rest.UseTypesAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_task_type_links_call(return_value):
    method_name = \
        'djautotask.api_rest.TaskTypeLinksAPIClient.get'
    return create_mock_call(method_name, return_value)


def service_api_get_account_types_call(return_value):
    method_name = 'djautotask.api_rest.AccountTypesAPIClient.get'
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

from suds.client import Client
from djautotask.tests import mocks, fixtures
from pathlib import Path

from djautotask import models
from djautotask import sync_rest as syncrest


def init_contacts():
    models.Contact.objects.all().delete()
    mocks.service_api_get_contacts_call(fixtures.API_CONTACT)
    synchronizer = syncrest.ContactSynchronizer()
    return synchronizer.sync()


def init_api_client():
    # Access the Autotask API's WSDL file from the tests directory
    # so that we can generate mock objects from the API without actually
    # calling the API.
    path = Path(__file__).parent / 'atws.wsdl'
    url = 'file://{}'.format(str(path))

    return Client(url)


# Set as a constant so the file only has to be opened once.
API_CLIENT = init_api_client()


def set_attributes(suds_object, fixture_object):
    """
    Set attributes on suds object from the given fixture.
    """
    for key, value in fixture_object.items():
        setattr(suds_object, key, value)

    return suds_object


def generate_api_objects(fixture_objects):
    """
    Generate multiple objects based on the given fixtures.
    """
    if fixture_objects is None:
        raise Exception("fixture_objects is empty.")

    fixture_result = {
        "items": [],
        "pageDetails": fixtures.API_PAGE_DETAILS
    }
    fixture_result["pageDetails"]["count"] = 0

    for fixture in fixture_objects:
        fixture_result["items"] += fixture["items"]
        fixture_result["pageDetails"]["count"] += len(fixture["items"])

    return fixture_result


def init_ticket_udfs():
    models.TicketUDF.objects.all().delete()
    mocks.service_api_get_ticket_udf_call(fixtures.API_UDF)
    synchronizer = syncrest.TicketUDFSynchronizer()
    return synchronizer.sync()


def init_task_udfs():
    models.TaskUDF.objects.all().delete()
    mocks.service_api_get_task_udf_call(fixtures.API_UDF)
    synchronizer = syncrest.TaskUDFSynchronizer()
    return synchronizer.sync()


def init_project_udfs():
    models.ProjectUDF.objects.all().delete()
    mocks.service_api_get_project_udf_call(fixtures.API_UDF)
    synchronizer = syncrest.ProjectUDFSynchronizer()
    return synchronizer.sync()


def init_project_statuses():
    models.ProjectStatus.objects.all().delete()
    mocks.service_api_get_project_picklist_call(
        fixtures.API_PROJECT_STATUS_FIELD)
    synchronizer = syncrest.ProjectStatusSynchronizer()
    return synchronizer.sync()


def init_project_types():
    models.ProjectType.objects.all().delete()
    mocks.service_api_get_project_picklist_call(
        fixtures.API_PROJECT_TYPE_FIELD)
    synchronizer = syncrest.ProjectTypeSynchronizer()
    return synchronizer.sync()


def init_display_colors():
    models.DisplayColor.objects.all().delete()
    mocks.service_api_get_ticket_category_picklist_call(
        fixtures.API_DISPLAY_COLOR_FIELD)
    synchronizer = syncrest.DisplayColorSynchronizer()
    return synchronizer.sync()


def init_issue_types():
    models.IssueType.objects.all().delete()
    mocks.service_api_get_ticket_picklist_call(fixtures.API_ISSUE_TYPE_FIELD)
    synchronizer = syncrest.IssueTypeSynchronizer()
    return synchronizer.sync()


def init_sub_issue_types():
    models.SubIssueType.objects.all().delete()
    mocks.service_api_get_ticket_picklist_call(
        fixtures.API_SUB_ISSUE_TYPE_FIELD)
    synchronizer = syncrest.SubIssueTypeSynchronizer()
    return synchronizer.sync()


def init_ticket_types():
    models.TicketType.objects.all().delete()
    mocks.service_api_get_ticket_picklist_call(
        fixtures.API_TICKET_TYPE_FIELD)
    synchronizer = syncrest.TicketTypeSynchronizer()
    return synchronizer.sync()


def init_statuses():
    models.Status.objects.all().delete()
    mocks.service_api_get_ticket_picklist_call(fixtures.API_STATUS_FIELD)
    synchronizer = syncrest.StatusSynchronizer()
    return synchronizer.sync()


def init_priorities():
    models.Priority.objects.all().delete()
    mocks.service_api_get_ticket_picklist_call(fixtures.API_PRIORITY_FIELD)
    synchronizer = syncrest.PrioritySynchronizer()
    return synchronizer.sync()


def init_queues():
    models.Queue.objects.all().delete()
    mocks.service_api_get_ticket_picklist_call(fixtures.API_QUEUE_FIELD)
    synchronizer = syncrest.QueueSynchronizer()
    return synchronizer.sync()


def init_sources():
    models.Source.objects.all().delete()
    mocks.service_api_get_ticket_picklist_call(fixtures.API_SOURCE_FIELD)
    synchronizer = syncrest.SourceSynchronizer()
    return synchronizer.sync()


def init_license_types():
    models.LicenseType.objects.all().delete()
    mocks.service_api_get_license_types_call(fixtures.API_LICENSE_TYPE_FIELD)
    synchronizer = syncrest.LicenseTypeSynchronizer()
    return synchronizer.sync()


def init_use_types():
    models.UseType.objects.all().delete()
    mocks.service_api_get_use_types_call(fixtures.API_USE_TYPE_FIELD)
    synchronizer = syncrest.UseTypeSynchronizer()
    return synchronizer.sync()


def init_task_type_links():
    models.TaskTypeLink.objects.all().delete()
    mocks.service_api_get_task_type_links_call(
        fixtures.API_TASK_TYPE_LINK_FIELD
    )
    synchronizer = syncrest.TaskTypeLinkSynchronizer()
    return synchronizer.sync()


def init_account_types():
    models.AccountType.objects.all().delete()
    mocks.service_api_get_account_types_call(fixtures.API_ACCOUNT_TYPE_FIELD)
    synchronizer = syncrest.AccountTypeSynchronizer()
    return synchronizer.sync()


def init_service_call_statuses():
    models.ServiceCallStatus.objects.all().delete()
    mocks.service_api_get_service_call_statuses_call(
        fixtures.API_SERVICE_CALL_STATUS_FIELD)
    synchronizer = syncrest.ServiceCallStatusSynchronizer()
    return synchronizer.sync()


def init_ticket_categories():
    models.TicketCategory.objects.all().delete()
    mocks.service_api_get_ticket_categories_call(fixtures.API_TICKET_CATEGORY)
    synchronizer = syncrest.TicketCategorySynchronizer()
    return synchronizer.sync()


def init_task_predecessors():
    models.TaskPredecessor.objects.all().delete()
    mocks.service_api_get_task_predecessors_call(fixtures.API_TASK_PREDECESSOR)
    synchronizer = syncrest.TaskPredecessorSynchronizer()
    return synchronizer.sync()


def init_tickets():
    models.Ticket.objects.all().delete()
    mocks.service_api_get_tickets_call(fixtures.API_TICKET)
    synchronizer = syncrest.TicketSynchronizer()
    return synchronizer.sync()


def init_resources():
    models.Resource.objects.all().delete()
    mocks.service_api_get_resources_call(fixtures.API_RESOURCE)
    synchronizer = syncrest.ResourceSynchronizer()
    return synchronizer.sync()


def init_ticket_secondary_resources():
    models.TicketSecondaryResource.objects.all().delete()
    mocks.service_api_get_ticket_secondary_resources_call(
        fixtures.API_TICKET_SECONDARY_RESOURCE)
    synchronizer = syncrest.TicketSecondaryResourceSynchronizer()
    return synchronizer.sync()


def init_task_secondary_resources():
    models.TaskSecondaryResource.objects.all().delete()
    mocks.service_api_get_task_secondary_resources_call(
        fixtures.API_TASK_SECONDARY_RESOURCE)
    synchronizer = syncrest.TaskSecondaryResourceSynchronizer()
    return synchronizer.sync()


def init_accounts():
    models.Account.objects.all().delete()
    mocks.service_api_get_accounts_call(fixtures.API_ACCOUNT)
    synchronizer = syncrest.AccountSynchronizer()
    return synchronizer.sync()


def init_account_physical_locations():
    models.AccountPhysicalLocation.objects.all().delete()
    mocks.service_api_get_account_physical_locations_call(
        fixtures.API_ACCOUNT_PHYSICAL_LOCATION
    )
    synchronizer = syncrest.AccountPhysicalLocationSynchronizer()
    return synchronizer.sync()


def init_projects():
    models.Project.objects.all().delete()
    mocks.service_api_get_projects_call(fixtures.API_PROJECT)
    synchronizer = syncrest.ProjectSynchronizer()
    return synchronizer.sync()


def init_phases():
    models.Phase.objects.all().delete()
    mocks.service_api_get_phases_call(fixtures.API_PHASE)
    synchronizer = syncrest.PhaseSynchronizer()
    return synchronizer.sync()


def init_tasks():
    models.Task.objects.all().delete()
    mocks.service_api_get_tasks_call(fixtures.API_TASK)
    synchronizer = syncrest.TaskSynchronizer()
    return synchronizer.sync()


def init_ticket_notes():
    mocks.create_mock_call(
        'djautotask.sync_rest.TicketNoteSynchronizer.create', None)

    models.TicketNote.objects.all().delete()
    mocks.service_api_get_ticket_notes_call(fixtures.API_TICKET_NOTE)
    synchronizer = syncrest.TicketNoteSynchronizer()
    return synchronizer.sync()


def init_task_notes():
    mocks.create_mock_call(
        'djautotask.sync_rest.TaskNoteSynchronizer.create', None)

    models.TaskNote.objects.all().delete()
    mocks.service_api_get_task_notes_call(fixtures.API_TASK_NOTE)
    synchronizer = syncrest.TaskNoteSynchronizer()
    return synchronizer.sync()


def init_note_types():
    models.NoteType.objects.all().delete()
    mocks.service_api_get_note_types_call(fixtures.API_NOTE_TYPE_FIELD)
    synchronizer = syncrest.NoteTypeSynchronizer()
    return synchronizer.sync()


def init_time_entries():
    models.TimeEntry.objects.all().delete()
    mocks.service_api_get_time_entries_call(fixtures.API_TIME_ENTRY)
    synchronizer = syncrest.TimeEntrySynchronizer()
    return synchronizer.sync()


def init_allocation_codes():
    models.AllocationCode.objects.all().delete()
    mocks.service_api_get_allocation_codes_call(fixtures.API_ALLOCATION_CODE)
    synchronizer = syncrest.AllocationCodeSynchronizer()
    return synchronizer.sync()


def init_roles():
    models.Role.objects.all().delete()
    mocks.service_api_get_roles_call(fixtures.API_ROLE)
    synchronizer = syncrest.RoleSynchronizer()
    return synchronizer.sync()


def init_departments():
    models.Department.objects.all().delete()
    mocks.service_api_get_departments_call(fixtures.API_DEPARTMENT)
    synchronizer = syncrest.DepartmentSynchronizer()
    return synchronizer.sync()


def init_resource_service_desk_roles():
    models.ResourceServiceDeskRole.objects.all().delete()
    mocks.service_api_get_resource_service_desk_roles_call(
        fixtures.API_RESOURCE_SERVICE_DESK_ROLE)
    synchronizer = syncrest.ResourceServiceDeskRoleSynchronizer()
    return synchronizer.sync()


def init_resource_role_departments():
    models.ResourceRoleDepartment.objects.all().delete()
    mocks.service_api_get_resource_role_departments_call(
        fixtures.API_RESOURCE_ROLE_DEPARTMENT)
    synchronizer = syncrest.ResourceRoleDepartmentSynchronizer()
    return synchronizer.sync()


def init_contracts():
    models.Contract.objects.all().delete()
    mocks.service_api_get_contracts_call(fixtures.API_CONTRACT)
    synchronizer = syncrest.ContractSynchronizer()
    return synchronizer.sync()


def init_service_calls():
    models.ServiceCall.objects.all().delete()
    mocks.service_api_get_service_calls_call(fixtures.API_SERVICE_CALL)
    synchronizer = syncrest.ServiceCallSynchronizer()
    return synchronizer.sync()


def init_service_call_tickets():
    models.ServiceCallTicket.objects.all().delete()
    mocks.service_api_get_service_call_tickets_call(
        fixtures.API_SERVICE_CALL_TICKET)
    synchronizer = syncrest.ServiceCallTicketSynchronizer()
    return synchronizer.sync()


def init_service_call_tasks():
    models.ServiceCallTask.objects.all().delete()
    mocks.service_api_get_service_call_tasks_call(
        fixtures.API_SERVICE_CALL_TASK)
    synchronizer = syncrest.ServiceCallTaskSynchronizer()
    return synchronizer.sync()


def init_service_call_ticket_resources():
    models.ServiceCallTicketResource.objects.all().delete()
    mocks.service_api_get_service_call_ticket_resources_call(
        fixtures.API_SERVICE_CALL_TICKET_RESOURCE)
    synchronizer = syncrest.ServiceCallTicketResourceSynchronizer()
    return synchronizer.sync()


def init_service_call_task_resources():
    models.ServiceCallTaskResource.objects.all().delete()
    mocks.service_api_get_service_call_task_resources_call(
        fixtures.API_SERVICE_CALL_TASK_RESOURCE)
    synchronizer = syncrest.ServiceCallTaskResourceSynchronizer()
    return synchronizer.sync()

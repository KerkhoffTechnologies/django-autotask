from suds.client import Client
from atws.wrapper import QueryCursor
from atws import helpers
from xml.etree import ElementTree
from djautotask import sync
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


def mock_query_generator(suds_objects):
    """
    A generator to return suds objects to mock the same behaviour as the
    ATWS Wrapper query method.
    """
    for obj in suds_objects:
        yield obj


def set_attributes(suds_object, fixture_object):
    """
    Set attributes on suds object from the given fixture.
    """
    for key, value in fixture_object.items():
        setattr(suds_object, key, value)

    return suds_object


# generate object for SOAP API
def generate_objects(object_type, fixture_objects):
    """
    Generate multiple objects based on the given fixtures.
    """
    client = API_CLIENT
    object_list = []

    if fixture_objects is None:
        raise Exception(object_type)

    # Create test suds objects from the list of fixtures.
    for fixture in fixture_objects:
        suds_object = \
            set_attributes(client.factory.create(object_type), fixture)

        object_list.append(suds_object)

    return QueryCursor(mock_query_generator(object_list))


# generate object for REST API
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


def generate_picklist_objects(object_type, fixture_objects):
    """
    Generate a mock ArrayOfField object that simulates an entity returned
    from the API with a picklist of objects.
    """
    client = API_CLIENT
    object_list = []
    array_of_field = client.factory.create('ArrayOfField')
    field = client.factory.create('Field')

    for fixture in fixture_objects:
        pick_list_value = client.factory.create('PickListValue')
        picklist_object = set_attributes(pick_list_value, fixture)
        object_list.append(picklist_object)

    # suds-community does not normally initialize the ArrayOfPickListValue
    # field because it is an optional field. We force it to by modifying the
    # test wsdl file for the "Field"'s PicklistValues, chagining its minOccurs
    # to "1", so it initializes it for us.
    field.Name = object_type
    field.IsPickList = True
    field.PicklistValues.PickListValue = object_list

    array_of_field[0].append(field)

    return array_of_field


def generate_udf_objects(fixture_objects):
    """
    Generate a mock ArrayOfField object that simulates an entity returned
    from the API with a picklist of objects.
    """
    client = API_CLIENT
    array_of_field = client.factory.create('ArrayOfField')

    for fixture in fixture_objects:
        field = client.factory.create('Field')
        field.Name = fixture['Name']
        field.Label = fixture['Label']
        field.Type = fixture['Type']
        field.Length = fixture['Length']
        field.IsPickList = fixture['IsPickList']

        if field.IsPickList:
            object_list = []
            for values in fixture['PicklistValues']:
                pick_list_value = client.factory.create('PickListValue')
                picklist_object = set_attributes(pick_list_value, values)
                object_list.append(picklist_object)
            field.PicklistValues.PickListValue = object_list

        # suds-community does not normally initialize the ArrayOfPickListValue
        # field because it is an optionalfield. We force it to by modifying the
        # test wsdl file forthe "Field"'sPicklistValues,chagining its minOccurs
        # to "1", so it initializes it for us.

        # field.Name = object_type
        # field.IsPickList = True

        array_of_field[0].append(field)

    return array_of_field


def manage_full_sync_return_data(value):
    """
    Generate and return objects based on the entity specified in the query.
    """
    fixture_dict = {
        'Ticket': fixtures.API_TICKET,
        'Resource': fixtures.API_RESOURCE_LIST,
        'TicketSecondaryResource': fixtures.API_SECONDARY_RESOURCE_LIST,
        'Account': fixtures.API_ACCOUNT_LIST,
        'AccountPhysicalLocation': fixtures.API_ACCOUNT_PHYSICAL_LOCATION_LIST,
        'Project': fixtures.API_PROJECT,
        'TicketCategory': fixtures.API_TICKET_CATEGORY_LIST,
        'Task': fixtures.API_TASK,
        'Phase': fixtures.API_PHASE_LIST,
        'TaskSecondaryResource': fixtures.API_TASK_SECONDARY_RESOURCE_LIST,
        'TicketNote': fixtures.API_TICKET_NOTE_LIST,
        'TaskNote': fixtures.API_TASK_NOTE_LIST,
        'TimeEntry': fixtures.API_TIME_ENTRY_LIST,
        'AllocationCode': fixtures.API_ALLOCATION_CODE_LIST,
        'Role': fixtures.API_ROLE,
        'Department': fixtures.API_DEPARTMENT,
        'ResourceRoleDepartment': fixtures.API_RESOURCE_ROLE_DEPARTMENT,
        'ResourceServiceDeskRole':
            fixtures.API_RESOURCE_SERVICE_DESK_ROLE,
        'Contract': fixtures.API_CONTRACT_LIST,
        'ServiceCall': fixtures.API_SERVICE_CALL_LIST,
        'ServiceCallTicket': fixtures.API_SERVICE_CALL_TICKET_LIST,
        'ServiceCallTask': fixtures.API_SERVICE_CALL_TASK_LIST,
        'ServiceCallTicketResource':
            fixtures.API_SERVICE_CALL_TICKET_RESOURCE_LIST,
        'ServiceCallTaskResource':
            fixtures.API_SERVICE_CALL_TASK_RESOURCE_LIST,
        'TaskPredecessor': fixtures.API_TASK_PREDECESSOR_LIST,
    }
    xml_value = ElementTree.fromstring(value.get_query_xml())
    object_type = xml_value.find('entity').text

    if object_type == 'TimeEntry':
        condition = xml_value.find('query').find('condition')

        # Ensure that a time entry gets returned with either an associated
        # task or ticket but not both.
        if condition.find('condition')[0].text == 'TaskID':
            fixture_dict['TimeEntry'] = [fixtures.API_TIME_ENTRY_TASK]
        else:
            fixture_dict['TimeEntry'] = [fixtures.API_TIME_ENTRY_TICKET]

    fixture = fixture_dict.get(object_type)
    return_value = generate_objects(object_type, fixture)

    return return_value


def manage_client_service_query_return_data(value):
    """
    Generate a complete ATWSResponse object and populate with entities
    specified in the query.
    """
    response = API_CLIENT.factory.create('ATWSResponse')
    response.ReturnCode = 1

    for entity in manage_full_sync_return_data(value):
        response.EntityResults.Entity.append(entity)

    result_count = helpers.query_result_count(response)
    return response, result_count


def manage_sync_picklist_return_data(wrapper, entity):
    """
    Generate and return picklist objects based on the entity
    specified in the query.
    """
    fixture_dict = {
        'Ticket': {
            'SubIssueType': fixtures.API_SUB_ISSUE_TYPE_LIST,
            'TicketType': fixtures.API_TICKET_TYPE_LIST,
        },
        'Project': {
            'Status': fixtures.API_PROJECT_STATUS_LIST,
            'Type': fixtures.API_PROJECT_TYPE_LIST,
        },
        'TicketNote': {
            'NoteType': fixtures.API_NOTE_TYPE_LIST,
        },
        'ServiceCall': {
            'Status': fixtures.API_SERVICE_CALL_STATUS_LIST,
        }
    }
    client = API_CLIENT
    array_of_field = client.factory.create('ArrayOfField')

    # Since get_field_info normally returns all fields on a given entity
    # as well as the picklists for picklist fields, we generate as many
    # picklist objects as we need and append to the array field.
    entity_fields = fixture_dict.get(entity)

    if entity_fields:
        for field_type, fixture in entity_fields.items():
            api_object = generate_picklist_objects(field_type, fixture)
            array_of_field[0].append(api_object[0][0])

    return array_of_field


def sync_objects(entity_type, fixture, sync_class):
    created_objects = generate_objects(
        entity_type, fixture
    )
    mocks.api_query_call(created_objects)
    synchronizer = sync_class()

    return synchronizer.sync()


def sync_picklist_objects(entity_type, fixture, sync_class):
    field_info = generate_picklist_objects(
        entity_type, fixture
    )
    mocks.api_picklist_call(field_info)
    synchronizer = sync_class()

    return synchronizer.sync()


def mock_udfs():
    field_info = generate_udf_objects(fixtures.API_UDF_LIST)
    mocks.api_udf_call(field_info)


def init_project_statuses():
    sync_picklist_objects(
        'Status',
        fixtures.API_PROJECT_STATUS_LIST,
        sync.ProjectStatusSynchronizer
    )


def init_project_types():
    sync_picklist_objects(
        'Type',
        fixtures.API_PROJECT_TYPE_LIST,
        sync.ProjectTypeSynchronizer
    )


def init_sub_issue_types():
    sync_picklist_objects(
        'SubIssueType',
        fixtures.API_SUB_ISSUE_TYPE_LIST,
        sync.SubIssueTypeSynchronizer
    )


def init_ticket_types():
    sync_picklist_objects(
        'TicketType',
        fixtures.API_TICKET_TYPE_LIST,
        sync.TicketTypeSynchronizer
    )


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
    sync_picklist_objects(
        'Status',
        fixtures.API_SERVICE_CALL_STATUS_LIST,
        sync.ServiceCallStatusSynchronizer
    )


def init_ticket_categories():
    sync_objects(
        'TicketCategory',
        fixtures.API_TICKET_CATEGORY_LIST,
        sync.TicketCategorySynchronizer
    )


def init_tickets():
    models.Ticket.objects.all().delete()
    mocks.service_api_get_tickets_call(fixtures.API_TICKET)
    synchronizer = syncrest.TicketSynchronizer()
    return synchronizer.sync()


def init_resources():
    sync_objects(
        'Resource',
        fixtures.API_RESOURCE_LIST,
        sync.ResourceSynchronizer
    )


def init_secondary_resources():
    sync_objects(
        'TicketSecondaryResource',
        fixtures.API_SECONDARY_RESOURCE_LIST,
        sync.TicketSecondaryResourceSynchronizer
    )


def init_accounts():
    sync_objects(
        'Account',
        fixtures.API_ACCOUNT_LIST,
        sync.AccountSynchronizer
    )


def init_account_physical_locations():
    sync_objects(
        'AccountPhysicalLocation',
        fixtures.API_ACCOUNT_PHYSICAL_LOCATION_LIST,
        sync.AccountPhysicalLocationSynchronizer
    )


def init_projects():
    models.Project.objects.all().delete()
    mocks.service_api_get_projects_call(fixtures.API_PROJECT)
    synchronizer = syncrest.ProjectSynchronizer()
    return synchronizer.sync()


def init_phases():
    sync_objects(
        'Phase',
        fixtures.API_PHASE_LIST,
        sync.PhaseSynchronizer
    )


def init_tasks():
    models.Task.objects.all().delete()
    mocks.service_api_get_tasks_call(fixtures.API_TASK)
    synchronizer = syncrest.TaskSynchronizer()
    return synchronizer.sync()


def init_task_secondary_resources():
    sync_objects(
        'TaskSecondaryResource',
        fixtures.API_TASK_SECONDARY_RESOURCE_LIST,
        sync.TaskSecondaryResourceSynchronizer
    )


def init_ticket_notes():
    mocks.create_mock_call(
        'djautotask.sync.TicketNoteSynchronizer._get_query_conditions', None)

    sync_objects(
        'TicketNote',
        fixtures.API_TICKET_NOTE_LIST,
        sync.TicketNoteSynchronizer
    )


def init_task_notes():
    mocks.create_mock_call(
        'djautotask.sync.TaskNoteSynchronizer._get_query_conditions', None)

    sync_objects(
        'TaskNote',
        fixtures.API_TASK_NOTE_LIST,
        sync.TaskNoteSynchronizer
    )


def init_note_types():
    sync_picklist_objects(
        'NoteType',
        fixtures.API_NOTE_TYPE_LIST,
        sync.NoteTypeSynchronizer
    )


def init_time_entries():
    sync_objects(
        'TimeEntry',
        fixtures.API_TIME_ENTRY_LIST,
        sync.TimeEntrySynchronizer
    )


def init_allocation_codes():
    sync_objects(
        'AllocationCode',
        fixtures.API_ALLOCATION_CODE_LIST,
        sync.AllocationCodeSynchronizer
    )


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
    sync_objects(
        'Contract',
        fixtures.API_CONTRACT_LIST,
        sync.ContractSynchronizer
    )


def init_service_calls():
    sync_objects(
        'ServiceCall',
        fixtures.API_SERVICE_CALL_LIST,
        sync.ServiceCallSynchronizer
    )


def init_service_call_tickets():
    sync_objects(
        'ServiceCallTicket',
        fixtures.API_SERVICE_CALL_TICKET_LIST,
        sync.ServiceCallTicketSynchronizer
    )


def init_service_call_tasks():
    sync_objects(
        'ServiceCallTask',
        fixtures.API_SERVICE_CALL_TASK_LIST,
        sync.ServiceCallTaskSynchronizer
    )


def init_task_predecessors():
    sync_objects(
        'TaskPredecessor',
        fixtures.API_TASK_PREDECESSOR_LIST,
        sync.TaskPredecessorSynchronizer
    )

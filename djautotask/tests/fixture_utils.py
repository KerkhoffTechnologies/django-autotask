from suds.client import Client
from atws.wrapper import QueryCursor
from atws import helpers
import urllib
from xml.etree import ElementTree
import os
from djautotask import sync
from djautotask.tests import mocks, fixtures


def init_api_client():
    # Access the Autotask API's WSDL file from the tests directory
    # so that we can generate mock objects from the API without actually
    # calling the API.
    path = os.path.abspath("djautotask/tests/atws.wsdl")
    url = urllib.parse.urljoin('file:', urllib.request.pathname2url(path))

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


def generate_objects(object_type, fixture_objects):
    """
    Generate multiple objects based on the given fixtures.
    """
    client = API_CLIENT
    object_list = []

    # Create test suds objects from the list of fixtures.
    for fixture in fixture_objects:
        suds_object = \
            set_attributes(client.factory.create(object_type), fixture)

        object_list.append(suds_object)

    return QueryCursor(mock_query_generator(object_list))


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

    field.Name = object_type
    field.IsPickList = True
    field.PicklistValues.PickListValue = object_list

    array_of_field[0].append(field)

    return array_of_field


def manage_full_sync_return_data(value):
    """
    Generate and return objects based on the entity specified in the query.
    """
    fixture_dict = {
        'Ticket': fixtures.API_TICKET_LIST,
        'Resource': fixtures.API_RESOURCE_LIST,
        'TicketSecondaryResource': fixtures.API_SECONDARY_RESOURCE_LIST,
        'Account': fixtures.API_ACCOUNT_LIST,
        'Project': fixtures.API_PROJECT_LIST,
        'TicketCategory': fixtures.API_TICKET_CATEGORY_LIST,
    }
    xml_value = ElementTree.fromstring(value.get_query_xml())
    object_type = xml_value.find('entity').text

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
            'Status': fixtures.API_TICKET_STATUS_LIST,
            'Priority': fixtures.API_TICKET_PRIORITY_LIST,
            'QueueID': fixtures.API_QUEUE_LIST,
            'Source': fixtures.API_SOURCE_LIST,
            'IssueType': fixtures.API_ISSUE_TYPE_LIST,
            'SubIssueType': fixtures.API_SUB_ISSUE_TYPE_LIST,
            'TicketType': fixtures.API_TICKET_TYPE_LIST,
        },
        'Project': {
            'Status': fixtures.API_PROJECT_STATUS_LIST,
            'Type': fixtures.API_PROJECT_TYPE_LIST,
        },
        'TicketCategory': {
            'DisplayColorRGB': fixtures.API_DISPLAY_COLOR_LIST,
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


def init_ticket_statuses():
    sync_picklist_objects(
        'Status',
        fixtures.API_TICKET_STATUS_LIST,
        sync.TicketStatusSynchronizer
    )


def init_ticket_priorities():
    sync_picklist_objects(
        'Priority',
        fixtures.API_TICKET_PRIORITY_LIST,
        sync.TicketPrioritySynchronizer
    )


def init_queues():
    sync_picklist_objects(
        'QueueID',
        fixtures.API_QUEUE_LIST,
        sync.QueueSynchronizer
    )


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


def init_sources():
    sync_picklist_objects(
        'Source',
        fixtures.API_SOURCE_LIST,
        sync.SourceSynchronizer
    )


def init_issue_types():
    sync_picklist_objects(
        'IssueType',
        fixtures.API_ISSUE_TYPE_LIST,
        sync.IssueTypeSynchronizer
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
    sync_picklist_objects(
        'DisplayColorRGB',
        fixtures.API_DISPLAY_COLOR_LIST,
        sync.DisplayColorSynchronizer
    )


def init_ticket_categories():
    sync_objects(
        'TicketCategory',
        fixtures.API_TICKET_CATEGORY_LIST,
        sync.TicketCategorySynchronizer
    )


def init_tickets():
    return sync_objects(
        'Ticket',
        fixtures.API_TICKET_LIST,
        sync.TicketSynchronizer
    )


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


def init_projects():
    sync_objects(
        'Project',
        fixtures.API_PROJECT_LIST,
        sync.ProjectSynchronizer
    )

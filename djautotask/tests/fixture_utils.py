from suds.client import Client
from atws.wrapper import QueryCursor
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
        'Account': fixtures.API_ACCOUNT_LIST
    }
    xml_value = ElementTree.fromstring(value.get_query_xml())
    object_type = xml_value.find('entity').text

    fixture = fixture_dict[object_type]
    return_value = generate_objects(object_type, fixture)

    return return_value


def manage_sync_picklist_return_data(wrapper, entity):
    """
    Generate and return picklist objects based on the entity
    specified in the query.
    """
    fixture_dict = {
        'Status': fixtures.API_TICKET_STATUS_LIST,
        'Priority': fixtures.API_TICKET_PRIORITY_LIST,
        'QueueID': fixtures.API_QUEUE_LIST,
    }
    client = API_CLIENT
    array_of_field = client.factory.create('ArrayOfField')

    # Since get_field_info normally returns all fields on a given entity
    # as well as the picklists for picklist fields, we generate as many
    # picklist objects as we need and append to the array field.
    for entity_type, fixture in fixture_dict.items():
        api_object = generate_picklist_objects(entity_type, fixture)
        array_of_field[0].append(api_object[0][0])

    return array_of_field


def init_ticket_statuses():
    field_info = generate_picklist_objects(
        'Status', fixtures.API_TICKET_STATUS_LIST
    )
    mocks.ticket_status_api_call(field_info)
    synchronizer = sync.TicketStatusSynchronizer()
    return synchronizer.sync()


def init_ticket_priorities():
    field_info = generate_picklist_objects(
        'Priority', fixtures.API_TICKET_PRIORITY_LIST
    )
    mocks.ticket_priority_api_call(field_info)
    synchronizer = sync.TicketPrioritySynchronizer()
    return synchronizer.sync()


def init_queues():
    field_info = generate_picklist_objects(
        'QueueID', fixtures.API_QUEUE_LIST
    )
    mocks.queue_api_call(field_info)
    synchronizer = sync.QueueSynchronizer()
    return synchronizer.sync()


def init_tickets():
    tickets = generate_objects('Ticket', fixtures.API_TICKET_LIST)

    mocks.ticket_api_call(tickets)
    synchronizer = sync.TicketSynchronizer()
    return synchronizer.sync()


def init_resources():
    tickets = generate_objects('Resource', fixtures.API_RESOURCE_LIST)

    mocks.resource_api_call(tickets)
    synchronizer = sync.ResourceSynchronizer()
    return synchronizer.sync()


def init_secondary_resources():
    secondary_resources = generate_objects(
        'TicketSecondaryResource', fixtures.API_SECONDARY_RESOURCE_LIST)

    mocks.secondary_resource_api_call(secondary_resources)
    synchronizer = sync.TicketSecondaryResourceSynchronizer()
    return synchronizer.sync()


def init_accounts():
    account = generate_objects('Account', fixtures.API_ACCOUNT_LIST)

    mocks.account_api_call(account)
    synchronizer = sync.AccountSynchronizer()
    return synchronizer.sync()

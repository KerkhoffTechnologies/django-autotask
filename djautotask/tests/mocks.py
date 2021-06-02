from mock import patch
from atws.query import Query
from djautotask.tests import fixtures
import json
import responses
from django.core.cache import cache


WRAPPER_QUERY_METHOD = 'atws.wrapper.Wrapper.query'
GET_FIELD_INFO_METHOD = 'atws.helpers.get_field_info'
GET_UDF_INFO_METHOD = 'atws.wrapper.Wrapper.get_udf_info'


def create_mock_call(method_name, return_value, side_effect=None):
    """Utility function for mocking the specified function or method"""
    _patch = patch(method_name, side_effect=side_effect)
    mock_get_call = _patch.start()

    if not side_effect:
        mock_get_call.return_value = return_value

    return mock_get_call, _patch


def init_api_connection(return_value):
    method_name = 'djautotask.api.init_api_connection'

    return create_mock_call(method_name, return_value)


def api_query_call(return_value):
    return create_mock_call(WRAPPER_QUERY_METHOD, return_value)


def api_picklist_call(return_value):
    return create_mock_call(GET_FIELD_INFO_METHOD, return_value)


def api_udf_call(return_value):
    return create_mock_call(GET_UDF_INFO_METHOD, return_value)


def wrapper_query_api_calls(side_effect=None):
    """
    Patch the Wrapper query method to return values based on the
    supplied side effect.
    """
    _patch = patch(WRAPPER_QUERY_METHOD, side_effect=side_effect)
    _patch.start()


def get_field_info_api_calls(side_effect=None):
    """
    Patch the get_info_field method to return values based on the
    supplied side effect.
    """
    _patch = patch(GET_FIELD_INFO_METHOD, side_effect=side_effect)
    _patch.start()


def generate_time_entry_queries(model_class, id_field, sync_job):
    query = Query('TimeEntry')
    query.WHERE('id', query.GreaterThanorEquals, 0)

    if id_field == 'TicketID':
        fixture_id = fixtures.API_TIME_ENTRY_TICKET['id']
    else:
        fixture_id = fixtures.API_TIME_ENTRY_TASK['id']

    query.open_bracket('AND')
    query.OR(id_field, query.Equals, fixture_id)
    query.close_bracket()
    return [query]


def build_batch_query(side_effect=None):

    mock_call, _patch = create_mock_call(
        'djautotask.sync.TimeEntrySynchronizer.build_batch_queries',
        [],
        side_effect=side_effect
    )
    return mock_call, _patch


def init_api_rest_connection(return_value=None):
    method_name = 'djautotask.api_rest.get_api_connection_url'
    cache.set('zone_info_url', return_value)
    return create_mock_call(method_name, return_value)


def service_api_get_contacts_call(return_value):
    method_name = 'djautotask.api_rest.ContactsAPIClient.get_contacts'
    return create_mock_call(method_name, return_value)


def service_api_get_tickets_call(return_value):
    method_name = 'djautotask.api_rest.TicketsAPIClient.get_tickets'
    return create_mock_call(method_name, return_value)


def service_api_get_ticket_call(return_value):
    method_name = 'djautotask.api_rest.TicketsAPIClient.get_ticket'
    return create_mock_call(method_name, return_value)


def service_api_get_tasks_call(return_value):
    method_name = 'djautotask.api_rest.TasksAPIClient.get_tasks'
    return create_mock_call(method_name, return_value)


def service_api_get_projects_call(return_value):
    method_name = 'djautotask.api_rest.ProjectsAPIClient.get_projects'
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

import datetime
import decimal
import json
import logging
from json import JSONDecodeError

import pytz
import requests

from django.conf import settings
from django.core.cache import cache
from django.db import models
from djautotask.utils import DjautotaskSettings
from retrying import retry

RETRY_WAIT_EXPONENTIAL_MULTAPPLIER = 1000  # Initial number of milliseconds to
# wait before retrying a request.
RETRY_WAIT_EXPONENTIAL_MAX = 10000  # Maximum number of milliseconds to wait
FORBIDDEN_ERROR_MESSAGE = \
    'The logged in Resource does not have the adequate ' \
    'permissions to create this entity type.'


logger = logging.getLogger(__name__)


class AutotaskAPIError(Exception):
    """Raise this, not request exceptions."""
    pass


class AutotaskAPIClientError(AutotaskAPIError):
    """
    Raise this to indicate any http error that falls within the
    4xx class of http status codes.
    """
    pass


class AutotaskAPIServerError(AutotaskAPIError):
    """
    Raise this to indicate a Server Error
    500 class of http status codes.
    """
    pass


class AutotaskRecordNotFoundError(AutotaskAPIClientError):
    """The record was not found."""
    pass


class AutotaskSecurityPermissionsException(AutotaskAPIClientError):
    """The API credentials have insufficient security permissions."""
    pass


def retry_if_api_error(exception):
    """
    Return True if we should retry (in this case when it's an
    AutotaskAPIError), False otherwise.

    Basically, don't retry on AutotaskAPIClientError, because those are the
    type of exceptions where retrying won't help (404s, 403s, etc).
    """
    return type(exception) is AutotaskAPIError


def get_cached_url(cache_key):
    return cache.get(cache_key)


def get_api_connection_url():
    return _get_connection_url('url')


def get_web_connection_url():
    return _get_connection_url('webUrl')


def _get_connection_url(field):
    cache_key = 'zone_info_' + field
    api_url_from_cache = get_cached_url(cache_key)

    if not api_url_from_cache:
        try:
            json_obj = get_zone_info(settings.AUTOTASK_CREDENTIALS['username'])
            url = json_obj[field]
            cache.set(cache_key, url, timeout=None)
        except AutotaskAPIError as e:
            raise AutotaskAPIError('Failed to get zone info: {}'.format(e))
    else:
        url = api_url_from_cache

    return url


def get_zone_info(username):
    endpoint_url = settings.AUTOTASK_SERVER_URL + 'v1.0/zoneInformation?user='\
                   + username

    try:
        logger.debug('Making GET request to {}'.format(endpoint_url))
        response = requests.get(endpoint_url)
        if 200 == response.status_code:
            resp_json = response.json()
            return resp_json
        elif 500 == response.status_code:
            # AT returns 500 if username is blank or incorrect.
            resp_json = response.json()
            raise AutotaskAPIError(
                'Request failed: GET {}: {}'.format(
                    endpoint_url, json.dumps(resp_json)
                )
            )
        else:
            raise AutotaskAPIError(response.content)
    except requests.RequestException as e:
        raise AutotaskAPIError(
            'Request failed: GET {}: {}'.format(
                endpoint_url, e
            )
        )


class ApiCondition:

    def __init__(self, *args, op=None, field=None, value=None):
        self._items = []
        self.op = op
        self.field = field
        self.value = value

        if op in ("and", "or"):
            # Grouping query
            for condition in args:
                if type(condition) != self.__class__:
                    raise TypeError(
                        "Grouped conditions must also be "
                        "instances of {}".format(self.__class__.__name__)
                    )
                self._items.append(condition)

    def __repr__(self):
        if len(self._items):
            return self._items.__repr__()
        return '{{op: {}, field: {}, value: {}}}'.format(
            self.op,
            self.field,
            self.value
        )

    def format_condition(self):
        if len(self._items):
            # Grouping Query
            condition = {
                "op": self.op,
                "items": [
                    api_condition.format_condition()
                    for api_condition in self._items
                ]
            }
        else:
            condition = {
                "op": self.op,
                "field": self.field
            }
            if self.value:
                # value is not required for non-comparison queries
                condition['value'] = self.value

        return condition


class ApiConditionList:
    METHODS = {
        'get': 'query?search=',
        'post': 'query'
    }

    def __init__(self):
        self._list = list()

    def __repr__(self):
        return self._list.__repr__()

    def __len__(self):
        return len(self._list)

    def __getitem__(self, i):
        return self._list[i]

    def __setitem__(self, i, value):
        if type(value) is not ApiCondition:
            raise TypeError("Conditions must be instances of ApiCondition.")
        self._list[i] = value

    def __delitem__(self, i):
        del self._list[i]

    def __iter__(self):
        return self._list.__iter__()

    def build_query(self, method="get"):
        queries = []
        for condition in self._list:
            queries.append(condition.format_condition())

        endpoint = self.METHODS[method]
        filters = json.dumps({'filter': queries})

        if method == "get":
            endpoint += filters
            filters = None
        elif method != "post":
            raise TypeError("Unsupported method")
        return endpoint, filters

    def add(self, condition):
        if type(condition) is not ApiCondition:
            raise TypeError("Conditions must be instances of ApiCondition.")

        self._list.append(condition)


class AutotaskAPIClient(object):
    API = None

    def __init__(
        self,
        username=None,
        password=None,
        integration_code=None,
        rest_api_version=None,
        server_url=None,
    ):
        if not username:
            username = settings.AUTOTASK_CREDENTIALS['username']
        if not password:
            password = settings.AUTOTASK_CREDENTIALS['password']
        if not integration_code:
            integration_code = settings.AUTOTASK_CREDENTIALS[
                'integration_code'
            ]
        if not rest_api_version:
            rest_api_version = settings.AUTOTASK_CREDENTIALS[
                'rest_api_version']
        if not server_url:
            server_url = get_api_connection_url()

        if not self.API:
            raise ValueError('API not specified')

        self.username = username
        self.password = password
        self.integration_code = integration_code
        self.rest_api_version = rest_api_version
        self.server_url = server_url

        self.request_settings = DjautotaskSettings().get_settings()
        self.timeout = self.request_settings['timeout']
        self.conditions = ApiConditionList()

        self.cached_body = None

    @property
    def api_base_url(self):
        return '{0}v{1}/'.format(
            self.server_url,
            settings.AUTOTASK_CREDENTIALS['rest_api_version'],
        )

    def get_api_url(self, endpoint=None):
        if not endpoint:
            endpoint = self.API

        return '{0}{1}/'.format(
            self.api_base_url,
            endpoint,
        )

    def _log_failed(self, response):
        logger.error('Failed API call: {0} - {1} - {2}'.format(
            response.url, response.status_code, response.content))

    def _prepare_error_response(self, response):
        error = response.content.decode("utf-8")
        # decode the bytes encoded error to a string
        # error = error.args[0].decode("utf-8")
        error = error.replace('\r\n', '')
        messages = []

        try:
            error = json.loads(error)
            stripped_message = error.get('message').rstrip('.') if \
                error.get('message') else 'No message'
            primary_error_msg = '{}.'.format(stripped_message)
            if error.get('errors'):
                for error_message in error.get('errors'):
                    messages.append(
                        '{}.'.format(error_message.rstrip('.'))
                    )

            messages = ' The error was: '.join(messages)

            msg = '{} {}'.format(primary_error_msg, messages)

        except json.decoder.JSONDecodeError:
            # JSON decoding failed
            msg = 'An error occurred: {} {}'.format(response.status_code,
                                                    error)
        except KeyError:
            # 'code' or 'message' was not found in the error
            msg = 'An error occurred: {} {}'.format(response.status_code,
                                                    error)
        return msg

    def get_headers(self):
        headers = {'Content-Type': 'application/json'}

        if self.username:
            headers['UserName'] = self.username
        if self.password:
            headers['Secret'] = self.password
        if self.integration_code:
            headers['ApiIntegrationCode'] = self.integration_code

        return headers

    def _format_fields(self, api_entity, inserted_fields):
        body = {'id': api_entity.id} if api_entity.id else dict()

        for field, value in inserted_fields.items():
            if field in api_entity.AUTOTASK_FIELDS:
                key = api_entity.AUTOTASK_FIELDS[field]
                body = self._format_request_body(body, key, value)

        return body

    def _format_request_body(self, body, key, value):
        if isinstance(value, datetime.datetime):
            body.update({
                key: value.astimezone(
                    pytz.timezone('UTC')).strftime(
                    "%Y-%m-%dT%H:%M:%SZ")
            })

        elif isinstance(value, models.Model):
            body.update({
                key: value.id
            })

        elif isinstance(value, decimal.Decimal):
            body.update(
                {key: str(value) if value else '0'}
            )

        else:
            body.update(
                {key: str(value) if value else ''}
            )

        return body

    def fetch_resource(self, next_url=None, retry_counter=None, method='get',
                       *args, **kwargs):
        """
        retry_counter is a dict in the form {'count': 0} that is passed in
        to verify the number of attempts that were made.
        """
        @retry(stop_max_attempt_number=self.request_settings['max_attempts'],
               wait_exponential_multiplier=RETRY_WAIT_EXPONENTIAL_MULTAPPLIER,
               wait_exponential_max=RETRY_WAIT_EXPONENTIAL_MAX,
               retry_on_exception=retry_if_api_error)
        def _fetch_resource(endpoint_url, request_retry_counter=None,
                            request_method=method, request_body=None,
                            **kwargs):
            if not request_retry_counter:
                request_retry_counter = {'count': 0}
            request_retry_counter['count'] += 1

            try:
                self.log_message(endpoint_url, request_method, request_body)

                response = requests.request(
                    request_method,
                    endpoint_url,
                    data=request_body,
                    timeout=self.timeout,
                    headers=self.get_headers(),
                )

            except requests.RequestException as e:
                logger.error('Request failed: {} {}: {}'.format(
                    request_method.upper(), endpoint_url, e))
                raise AutotaskAPIError('{}'.format(e))

            if 200 <= response.status_code < 300:
                try:
                    return response.json()
                except JSONDecodeError as e:
                    raise AutotaskAPIError('{}'.format(e))
            elif response.status_code == 403:
                self._log_failed(response)
                raise AutotaskSecurityPermissionsException(
                    self._prepare_error_response(response),
                    response.status_code)
            elif 400 <= response.status_code < 499:
                self._log_failed(response)
                raise AutotaskAPIClientError(
                    self._prepare_error_response(response))
            elif response.status_code == 500:
                self._log_failed(response)
                raise AutotaskAPIServerError(
                    self._prepare_error_response(response))
            else:
                self._log_failed(response)
                raise AutotaskAPIError(
                    self._prepare_error_response(response))

        if next_url:
            url = next_url
        else:
            # Query endpoint is different between GET and POST
            query_endpoint, self.cached_body = \
                self.conditions.build_query(method=method)
            url = "{}{}".format(self.get_api_url(), query_endpoint)

        return _fetch_resource(
            url, request_retry_counter=retry_counter,
            request_method=method, request_body=self.cached_body, **kwargs)

    def log_message(self, endpoint, method, body):
        body = body if body else ''

        logger_message = \
            'Making {} request to {}'.format(method.upper(), endpoint)
        if method == 'post':
            logger_message = \
                '{}. Request body: {}'.format(logger_message, body)

        logger.debug(logger_message)

    def request(self, method, endpoint_url, body=None):
        """
        Issue the given type of request to the specified REST endpoint.
        """
        try:
            logger.debug(
                'Making {} request to {}'.format(method, endpoint_url)
            )
            response = requests.request(
                method,
                endpoint_url,
                json=body,
                timeout=self.timeout,
                headers=self.get_headers(),
            )
        except requests.RequestException as e:
            logger.error(
                'Request failed: {} {}: {}'.format(method, endpoint_url, e)
            )
            raise AutotaskAPIError('{}'.format(e))

        if response.status_code == 204:  # No content
            return None
        elif 200 <= response.status_code < 300:
            return response.json()
        elif response.status_code == 403:
            self._log_failed(response)
            raise AutotaskSecurityPermissionsException(
                self._prepare_error_response(response), response.status_code)
        elif response.status_code == 404:
            msg = 'Resource not found: {}'.format(response.url)
            logger.warning(msg)
            raise AutotaskRecordNotFoundError(msg)
        elif 400 <= response.status_code < 499:
            self._log_failed(response)
            raise AutotaskAPIClientError(
                self._prepare_error_response(response))
        elif response.status_code == 500:
            self._log_failed(response)
            prepared_error = self._prepare_error_response(response)

            # As of Aug. 2021, the REST API returns HTTP 500 for some
            # insufficient permission cases (updating checklist items)
            # even though the docs state that HTTP 403 should be returned.
            # https://webservices2.autotask.net/atservicesrest/swagger/ui/index#/TicketChecklistItemsChild/TicketChecklistItemsChild_CreateEntity # noqa
            # Until this is fixed in the API, check for the message indicating
            # a permission error and raise an appropriate exception.
            if FORBIDDEN_ERROR_MESSAGE in prepared_error:
                raise AutotaskSecurityPermissionsException(prepared_error, 403)
            else:
                raise AutotaskAPIServerError(prepared_error)
        else:
            self._log_failed(response)
            raise AutotaskAPIError(response)

    def add_condition(self, condition):
        self.conditions.add(condition)

    def get_conditions(self):
        return self.conditions

    def remove_condtion(self, index):
        del self.conditions[index]

    def clear_conditions(self):
        self.conditions = ApiConditionList()

    def get(self, next_url, *args, **kwargs):
        return self.fetch_resource(next_url, *args, **kwargs)

    def get_single(self, instance_id):
        endpoint_url = '{}{}'.format(self.get_api_url(), instance_id)
        return self.fetch_resource(endpoint_url)

    def update(self, instance, changed_fields):
        body = self._format_fields(instance, changed_fields)
        return self.request('patch', self.get_api_url(), body)

    def create(self, instance, **kwargs):
        body = self._format_fields(instance, kwargs)
        # API returns only newly created id
        response = self.request('post', self.get_api_url(), body)
        return response.get('itemId')


class ChildAPIMixin:
    PARENT_API = None
    CHILD_API = None

    def get_child_url(self, parent_id):
        return '{}{}/{}/{}'.format(
            self.api_base_url,
            self.PARENT_API,
            parent_id,
            self.CHILD_API
        )

    def update(self, instance, parent, changed_fields):
        # Only for updating records with models in the DB, not Dummy syncs
        endpoint_url = self.get_child_url(parent.id)
        body = self._format_fields(instance, changed_fields)
        return self.request('patch', endpoint_url, body)

    def create(self, instance, parent, **kwargs):
        endpoint_url = self.get_child_url(parent.id)
        body = self._format_fields(instance, kwargs)
        response = self.request('post', endpoint_url, body)
        return response.get('itemId')


class ContactsAPIClient(AutotaskAPIClient):
    API = 'Contacts'


class RolesAPIClient(AutotaskAPIClient):
    API = 'Roles'


class DepartmentsAPIClient(AutotaskAPIClient):
    API = 'Departments'


class ResourceServiceDeskRolesAPIClient(AutotaskAPIClient):
    API = 'ResourceServiceDeskRoles'


class ResourceRoleDepartmentsAPIClient(AutotaskAPIClient):
    API = 'ResourceRoleDepartments'


class TicketsAPIClient(AutotaskAPIClient):
    API = 'Tickets'


class TasksAPIClient(ChildAPIMixin, AutotaskAPIClient):
    API = 'Tasks'
    PARENT_API = 'Projects'
    CHILD_API = API
    # For tasks, child API endpoint is the same

    def get(self, next_url, *args, **kwargs):
        """
        Fetch tasks from the API. We use a POST request to avoid URL length
        issues for cases where there are a large number of open projects in
        the database.
        """
        return self.fetch_resource(next_url, method='post', *args, **kwargs)


class ProjectsAPIClient(AutotaskAPIClient):
    API = 'Projects'

    # use POST method because of IN-clause query string
    def get(self, next_url, *args, **kwargs):
        return self.fetch_resource(next_url, method='post', *args, **kwargs)


class ServiceCallsAPIClient(AutotaskAPIClient):
    API = 'ServiceCalls'


class ServiceCallTicketsAPIClient(ChildAPIMixin, AutotaskAPIClient):
    API = 'ServiceCallTickets'
    PARENT_API = 'ServiceCalls'
    CHILD_API = 'Tickets'

    def create(self, instance, **kwargs):
        parent = kwargs.pop('service_call')
        return super().create(instance, parent, **kwargs)


class ServiceCallTicketResourcesAPIClient(ChildAPIMixin, AutotaskAPIClient):
    API = 'ServiceCallTicketResources'
    PARENT_API = 'ServiceCallTickets'
    CHILD_API = 'Resources'

    def create(self, instance, **kwargs):
        parent = kwargs.pop('service_call_ticket')
        return super().create(instance, parent, **kwargs)


class ServiceCallTasksAPIClient(ChildAPIMixin, AutotaskAPIClient):
    API = 'ServiceCallTasks'
    PARENT_API = 'ServiceCalls'
    CHILD_API = 'Tasks'

    def create(self, instance, **kwargs):
        parent = kwargs.pop('service_call')
        return super().create(instance, parent, **kwargs)


class ServiceCallTaskResourcesAPIClient(ChildAPIMixin, AutotaskAPIClient):
    API = 'ServiceCallTaskResources'
    PARENT_API = 'ServiceCallTasks'
    CHILD_API = 'Resources'

    def create(self, instance, **kwargs):
        parent = kwargs.pop('service_call_task')
        return super().create(instance, parent, **kwargs)


class AutotaskPicklistAPIClient(AutotaskAPIClient):

    def __init__(self, **kwargs):
        self.API = '{}/entityInformation/fields'.format(self.API_ENTITY)
        super().__init__(**kwargs)

    def get(self, next_url, *args, **kwargs):
        # Get either the next_url provided by the AT response or build the
        # initial url.
        return self.fetch_resource(
            next_url or self.get_api_url(), *args, **kwargs)


class LicenseTypesAPIClient(AutotaskPicklistAPIClient):
    API_ENTITY = 'Resources'


class UseTypesAPIClient(AutotaskPicklistAPIClient):
    API_ENTITY = 'BillingCodes'


class TaskTypeLinksAPIClient(AutotaskPicklistAPIClient):
    API_ENTITY = 'TimeEntries'


class AccountTypesAPIClient(AutotaskPicklistAPIClient):
    API_ENTITY = 'Companies'


class TicketCategoryPicklistAPIClient(AutotaskPicklistAPIClient):
    API_ENTITY = 'TicketCategories'


class ServiceCallStatusPicklistAPIClient(AutotaskPicklistAPIClient):
    API_ENTITY = 'ServiceCalls'


class TicketPicklistAPIClient(AutotaskPicklistAPIClient):
    API_ENTITY = 'Tickets'


class TicketChecklistItemsAPIClient(ChildAPIMixin, AutotaskAPIClient):
    API = 'TicketChecklistItems'
    PARENT_API = 'Tickets'
    CHILD_API = 'ChecklistItems'

    def update(self, parent, **kwargs):
        endpoint_url = self.get_child_url(parent)
        return self.request('patch', endpoint_url, kwargs)

    def create(self, parent, **kwargs):
        endpoint_url = self.get_child_url(parent)
        return self.request('post', endpoint_url, kwargs)

    def delete(self, parent, **kwargs):
        endpoint_url = '{}/{}'.format(
            self.get_child_url(parent),
            kwargs.get("id")
        )
        return self.request('delete', endpoint_url)

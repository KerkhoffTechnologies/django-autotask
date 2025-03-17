import datetime
import decimal
import json
import logging
from json import JSONDecodeError

import pytz
import requests
from django.apps import apps
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from djautotask.utils import DjautotaskSettings, encode_file_to_base64
from retrying import retry

RETRY_WAIT_EXPONENTIAL_MULTAPPLIER = 1000  # Initial number of milliseconds to
# wait before retrying a request.
RETRY_WAIT_EXPONENTIAL_MAX = 10000  # Maximum number of milliseconds to wait
CACHE_TIMEOUT = 43200
AT_URL_KEY = 'url'
AT_WEB_KEY = 'webUrl'
FORBIDDEN_ERROR_MESSAGE = \
    'The logged in Resource does not have the adequate permissions'
NO_RECORD_ERROR_MESSAGE = \
    'No message. No matching records found. The logged in Resource may not ' \
    'have the required permissions to delete the data.'

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


class AutotaskImpersonationLimitedException(
    AutotaskSecurityPermissionsException
):
    """The impersonation resource has insufficient security permissions."""
    pass


def parse_autotaskapierror(e):
    return ', '.join(e.args)


def retry_if_api_error(exception):
    """
    Return True if we should retry (in this case when it's an
    AutotaskAPIError), False otherwise.

    Basically, don't retry on AutotaskAPIClientError, because those are the
    type of exceptions where retrying won't help (404s, 403s, etc).
    """
    return type(exception) is AutotaskAPIError


def get_cached_url(cache_key):
    return cache.get(f'zone_{cache_key}')


def update_cache(json_obj):
    # set cache timeout as 10 minutes (default: 300)
    cache.set(
        f'zone_{AT_URL_KEY}', json_obj[AT_URL_KEY], timeout=CACHE_TIMEOUT)
    cache.set(
        f'zone_{AT_WEB_KEY}', json_obj[AT_WEB_KEY], timeout=CACHE_TIMEOUT)


def get_api_connection_url(username, force_fetch=False):
    try:
        return _get_connection_url(AT_URL_KEY, username, force_fetch)
    except AutotaskAPIError as e:
        # Save a log even when the get_zone_info request fails.
        SyncJob = apps.get_model('djautotask', 'SyncJob')
        sync_job = SyncJob()
        sync_job.start_time = timezone.now()
        sync_job.message = e
        sync_job.success = False
        sync_job.save()


def get_web_connection_url(username, force_fetch=False):
    return _get_connection_url(AT_WEB_KEY, username, force_fetch)


def _get_connection_url(field, username, force_fetch=False):
    api_url_from_cache = get_cached_url(field)

    if not api_url_from_cache or force_fetch:
        try:
            json_obj = get_zone_info(username)
            # Update cache if empty or forced
            update_cache(json_obj)

            url = json_obj[field]
        except AutotaskAPIError as e:
            raise AutotaskAPIError(f'Failed to get zone info: {e}')
    else:
        url = api_url_from_cache

    return url


def get_zone_info(username):
    endpoint_url = '{}v1.0/zoneInformation?user={}'.format(
        settings.AUTOTASK_SERVER_URL, username
    )

    try:
        logger.debug('Making GET request to {}'.format(endpoint_url))
        response = requests.get(endpoint_url, timeout=3)
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
                if not isinstance(condition, self.__class__):
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
        if not isinstance(value, ApiCondition):
            raise TypeError("Conditions must be instances of ApiCondition.")
        self._list[i] = value

    def __delitem__(self, i):
        del self._list[i]

    def __iter__(self):
        return self._list.__iter__()

    def build_query(self, method="get", **kwargs):
        queries = []
        for condition in self._list:
            queries.append(condition.format_condition())

        condition_filters = {
            'filter': queries,
        }

        max_records = kwargs.get('page_size')
        if max_records:
            condition_filters.update({
                'MaxRecords': max_records
            })

        endpoint = self.METHODS[method]
        filters = json.dumps(condition_filters)

        if method == "get":

            count = kwargs.get('record_count')
            if count:
                endpoint = f'query/count?search={filters}'
            else:
                endpoint += filters

            filters = None
        elif method != "post":
            raise TypeError("Unsupported method")

        return endpoint, filters

    def add(self, condition):
        if not isinstance(condition, ApiCondition):
            raise TypeError("Conditions must be instances of ApiCondition.")

        self._list.append(condition)


class AutotaskAPIClient(object):
    API = None
    MAX_401_ATTEMPTS = 1

    def __init__(
        self,
        username=None,
        password=None,
        integration_code=None,
        rest_api_version=None,
        server_url=None,
        impersonation_resource=None,
    ):
        if not username:
            username = settings.AUTOTASK_CREDENTIALS['username']
        if not password:
            password = settings.AUTOTASK_CREDENTIALS['password']
        if not integration_code:
            integration_code = \
                settings.AUTOTASK_CREDENTIALS['integration_code']
        if not rest_api_version:
            rest_api_version = \
                settings.AUTOTASK_CREDENTIALS['rest_api_version']
        if not server_url:
            server_url = get_api_connection_url(username)

        if not self.API:
            raise ValueError('API not specified')

        self.username = username
        self.password = password
        self.integration_code = integration_code
        self.rest_api_version = rest_api_version
        self.server_url = server_url

        self.request_settings = DjautotaskSettings().get_settings()
        self.timeout = self.request_settings['timeout']
        self.impersonation_resource = impersonation_resource
        self.conditions = ApiConditionList()

        self.cached_body = None

    @property
    def api_base_url(self):
        return '{0}v{1}/'.format(
            self.server_url,
            self.rest_api_version,
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

    def _prepare_error_for_impersonation(self, msg):
        impersonation_error_msg = \
            'Resource impersonation is enabled in your TopLeft ' \
            'application. Please check the resource security level that is ' \
            'being impersonated.'
        msg = '{} {}'.format(msg, impersonation_error_msg)
        return msg

    def _prepare_error_response(self, response):
        error = response.content.decode("utf-8")
        # decode the bytes encoded error to a string
        # error = error.args[0].decode("utf-8")
        error = error.replace('\r\n', '')

        try:
            error_json = json.loads(error)
            error_list = error_json.get('errors', [])
            if len(error_list) > 1:
                msg = 'Errors: {}'.format(', '.join(error_list))
            elif len(error_list) == 1:
                msg = error_list[0]
            else:
                # No errors given
                msg = 'No error message given.'
        except json.decoder.JSONDecodeError:
            # JSON decoding failed
            msg = 'An error occurred: {} {}'.format(response.status_code,
                                                    error)
        except KeyError:
            # 'code' or 'message' was not found in the error
            msg = 'An error occurred: {} {}'.format(response.status_code,
                                                    error)
        return msg

    def get_headers(self, method):
        headers = {'Content-Type': 'application/json'}

        if self.username:
            headers['UserName'] = self.username
        if self.password:
            headers['Secret'] = self.password
        if self.integration_code:
            headers['ApiIntegrationCode'] = self.integration_code
        if self.impersonation_resource and method.upper() != 'GET':
            # We don't check the impersonation possibility for GET request.
            self.check_impersonation_possibility()
            headers['ImpersonationResourceId'] = str(
                self.impersonation_resource.id
            ) if self.impersonation_resource else None

        return headers

    def _format_fields(self, record, inserted_fields):
        body = {'id': record.id} if record.id else dict()

        for field, value in inserted_fields.items():
            key = field
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

        elif isinstance(value, bool):
            body.update(
                {key: value}
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
                    headers=self.get_headers(request_method),
                )

            except requests.RequestException as e:
                logger.error('Request failed: {} {}: {}'.format(
                    request_method.upper(), endpoint_url, e))
                raise AutotaskAPIError('{}'.format(e))

            if 200 <= response.status_code < 300:
                try:
                    return response.json()
                except JSONDecodeError as e:
                    logger.error(
                        'Request failed during JSON decode: {} {}: {}'.format(
                            request_method.upper(), endpoint_url, e)
                    )
                    raise AutotaskAPIError('{}'.format(e))

            elif response.status_code == 401:
                # It could be the case that zone info has been changed
                msg = 'Unauthorized request: {}'.format(endpoint_url)
                logger.warning(msg)
                if request_retry_counter['count'] <= self.MAX_401_ATTEMPTS:
                    cached_url = get_cached_url(AT_URL_KEY)
                    if cached_url != get_api_connection_url(
                            self.username, force_fetch=True
                    ):
                        logger.info('Zone information has been changed, '
                                    'so this request will be retried.')
                        raise AutotaskAPIError(response.content)
                raise AutotaskAPIClientError(msg)
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
                msg = self._prepare_error_response(response)
                if FORBIDDEN_ERROR_MESSAGE in msg:
                    # Standards, who needs em?
                    raise AutotaskSecurityPermissionsException(msg)
                else:
                    raise AutotaskAPIServerError(
                        self._prepare_error_response(response)
                    )
            else:
                self._log_failed(response)
                raise AutotaskAPIError(
                    self._prepare_error_response(response))

        if next_url:
            url = next_url
        else:
            # Query endpoint is different between GET and POST
            query_endpoint, self.cached_body = \
                self.conditions.build_query(method=method, **kwargs)
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

    def check_impersonation_possibility(self):
        if self.impersonation_resource and not self.impersonation_resource.\
                license_type.has_impersonation(self):
            raise AutotaskImpersonationLimitedException(
                'You do not have the adequate permissions '
                '(impersonation limitation).')

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
                headers=self.get_headers(method),
            )
        except AutotaskImpersonationLimitedException as e:
            logger.error(
                'Request failed: {} {}: {}'.format(method, endpoint_url, e)
            )
            raise e
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
            # In addition, AT returns 500 when requested record doesn't exist
            # during the deletion
            if FORBIDDEN_ERROR_MESSAGE in prepared_error:
                if self.impersonation_resource:
                    prepared_error = self._prepare_error_for_impersonation(
                        prepared_error
                    )
                raise AutotaskSecurityPermissionsException(prepared_error)
            elif NO_RECORD_ERROR_MESSAGE in prepared_error:
                raise AutotaskRecordNotFoundError(prepared_error, 404)
            else:
                raise AutotaskAPIServerError(prepared_error)
        else:
            self._log_failed(response)
            raise AutotaskAPIError(response)

    def add_condition(self, condition):
        self.conditions.add(condition)
        return len(self.conditions) - 1

    def get_conditions(self):
        return self.conditions

    def remove_condition(self, index):
        del self.conditions[index]

    def clear_conditions(self):
        self.conditions = ApiConditionList()

    def get(self, next_url, *args, **kwargs):
        return self.fetch_resource(next_url, *args, **kwargs)

    def get_single(self, instance_id):
        endpoint_url = '{}{}'.format(self.get_api_url(), instance_id)
        response = self.fetch_resource(endpoint_url)
        if not response['item']:
            msg = 'Resource not found: {}'.format(endpoint_url)
            logger.warning(msg)
            raise AutotaskRecordNotFoundError(msg)
        return response

    def update(self, instance, changed_fields):
        body = self._format_fields(instance, changed_fields)
        return self.request('patch', self.get_api_url(), body)

    def create(self, instance, **kwargs):
        body = self._format_fields(instance, kwargs)
        # API returns only newly created id
        response = self.request('post', self.get_api_url(), body)
        return response.get('itemId')

    def delete(self, instance, parent=None):
        endpoint_url = self.get_api_url() + str(instance.id)
        response = self.request('delete', endpoint_url)
        # AT sends deleted_id or 500 in the case failure instead of 404 or 204
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
        endpoint_url = self.get_child_url(parent.id)
        body = self._format_fields(instance, changed_fields)
        return self.request('patch', endpoint_url, body)

    def create(self, instance, parent, **kwargs):
        endpoint_url = self.get_child_url(parent.id)
        body = self._format_fields(instance, kwargs)
        response = self.request('post', endpoint_url, body)
        return response.get('itemId')

    def delete(self, instance, parent):
        endpoint_url = '{}/{}'.format(
            self.get_child_url(parent.id),
            str(instance.id)
        )
        response = self.request('delete', endpoint_url)
        # AT sends deleted_id or 500 in the case failure instead of 404 or 204
        return response.get('itemId')

    # use POST method because of IN-clause query string
    def get(self, next_url, *args, **kwargs):
        return self.fetch_resource(next_url, method='post', *args, **kwargs)


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

    def count(self, next_url, *args, **kwargs):
        # Make get request using Api conditions
        return self.fetch_resource(next_url, *args, **kwargs)


class BillingCodesAPIClient(AutotaskAPIClient):
    API = 'BillingCodes'


class ContractsAPIClient(AutotaskAPIClient):
    API = 'Contracts'


class ContractExclusionSetAPIClient(AutotaskAPIClient):
    API = 'ContractExclusionSets'


class ContractsExcludedWorkTypeAPIClient(AutotaskAPIClient):
    API = 'ContractExclusionSetExcludedWorkTypes'


class ContractsExcludedRoleAPIClient(AutotaskAPIClient):
    API = 'ContractExclusionSetExcludedRoles'


class AccountPhysicalLocationsAPIClient(AutotaskAPIClient):
    API = 'CompanyLocations'

    # use POST method because of IN-clause query string
    def get(self, next_url, *args, **kwargs):
        return self.fetch_resource(next_url, method='post', *args, **kwargs)


class TasksAPIClient(ChildAPIMixin, AutotaskAPIClient):
    API = 'Tasks'
    PARENT_API = 'Projects'
    CHILD_API = API
    # For tasks, child API endpoint is the same


class TicketNotesAPIClient(ChildAPIMixin, AutotaskAPIClient):
    API = 'TicketNotes'
    PARENT_API = 'Tickets'
    CHILD_API = 'Notes'


class TaskNotesAPIClient(AutotaskAPIClient):
    API = 'TaskNotes'

    # use POST method because of IN-clause query string
    def get(self, next_url, *args, **kwargs):
        return self.fetch_resource(next_url, method='post', *args, **kwargs)


class TimeEntriesAPIClient(AutotaskAPIClient):
    API = 'TimeEntries'

    # use POST method because of IN-clause query string
    def get(self, next_url, *args, **kwargs):
        return self.fetch_resource(next_url, method='post', *args, **kwargs)


class TicketSecondaryResourcesAPIClient(ChildAPIMixin, AutotaskAPIClient):
    API = 'TicketSecondaryResources'
    PARENT_API = 'Tickets'
    CHILD_API = 'SecondaryResources'


class TaskSecondaryResourcesAPIClient(ChildAPIMixin, AutotaskAPIClient):
    API = 'TaskSecondaryResources'
    PARENT_API = 'Tasks'
    CHILD_API = 'SecondaryResources'


class ProjectsAPIClient(AutotaskAPIClient):
    API = 'Projects'

    # use POST method because of IN-clause query string
    def get(self, next_url, *args, **kwargs):
        return self.fetch_resource(next_url, method='post', *args, **kwargs)


class TicketCategoriesAPIClient(AutotaskAPIClient):
    API = 'TicketCategories'


class CompanyAlertAPIClient(AutotaskAPIClient):
    API = 'CompanyAlerts'

    def get(self, next_url=None, *args, **kwargs):
        if not next_url:
            search_filter = {"filter": [{"op": "exist", "field": "companyID"}]}
            next_url = (
                f"{self.api_base_url}/{self.API}/query?search="
                f"{json.dumps(search_filter)}"
            )
        return self.fetch_resource(next_url, *args, **kwargs)


class ProjectNotesAPIClient(AutotaskAPIClient):
    API = 'ProjectNotes'


class TaskPredecessorsAPIClient(AutotaskAPIClient):
    API = 'TaskPredecessors'

    # use POST method because of IN-clause query string
    def get(self, next_url, *args, **kwargs):
        return self.fetch_resource(next_url, method='post', *args, **kwargs)


class ServiceCallsAPIClient(AutotaskAPIClient):
    API = 'ServiceCalls'

    # use POST method because of IN-clause query string
    def get(self, next_url, *args, **kwargs):
        return self.fetch_resource(next_url, method='post', *args, **kwargs)


class ServiceCallTicketsAPIClient(ChildAPIMixin, AutotaskAPIClient):
    API = 'ServiceCallTickets'
    PARENT_API = 'ServiceCalls'
    CHILD_API = 'Tickets'


class ServiceCallTicketResourcesAPIClient(ChildAPIMixin, AutotaskAPIClient):
    API = 'ServiceCallTicketResources'
    PARENT_API = 'ServiceCallTickets'
    CHILD_API = 'Resources'


class ServiceCallTasksAPIClient(ChildAPIMixin, AutotaskAPIClient):
    API = 'ServiceCallTasks'
    PARENT_API = 'ServiceCalls'
    CHILD_API = 'Tasks'


class ServiceCallTaskResourcesAPIClient(ChildAPIMixin, AutotaskAPIClient):
    API = 'ServiceCallTaskResources'
    PARENT_API = 'ServiceCallTasks'
    CHILD_API = 'Resources'


class ResourcesAPIClient(AutotaskAPIClient):
    API = 'Resources'


class AccountsAPIClient(AutotaskAPIClient):
    API = 'Companies'


class PhasesAPIClient(AutotaskAPIClient):
    API = 'Phases'


class UDFAPIClient(AutotaskAPIClient):

    def get_api_url(self, endpoint=None):
        return '{0}{1}/entityInformation/userDefinedFields'.format(
            self.api_base_url,
            self.API,
        )


class TicketsUDFAPIClient(UDFAPIClient):
    API = 'Tickets'


class TasksUDFAPIClient(UDFAPIClient):
    API = 'Tasks'


class ProjectsUDFAPIClient(UDFAPIClient):
    API = 'Projects'


class AutotaskPicklistAPIClient(AutotaskAPIClient):

    def __init__(self, **kwargs):
        self.API = '{}/entityInformation/fields'.format(self.API_ENTITY)
        super().__init__(**kwargs)

    def get(self, next_url, *args, **kwargs):
        # Get either the next_url provided by the AT response or build the
        # initial url.
        return self.fetch_resource(
            next_url or self.get_api_url(), *args, **kwargs)


class NoteTypesAPIClient(AutotaskPicklistAPIClient):
    API_ENTITY = 'TicketNotes'


class LicenseTypesAPIClient(AutotaskPicklistAPIClient):
    API_ENTITY = 'Resources'


class UseTypesAPIClient(AutotaskPicklistAPIClient):
    API_ENTITY = 'BillingCodes'


class BillingCodeTypeAPIClient(AutotaskPicklistAPIClient):
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


class TaskPicklistAPIClient(AutotaskPicklistAPIClient):
    API_ENTITY = 'Tasks'


class ProjectPicklistAPIClient(AutotaskPicklistAPIClient):
    API_ENTITY = 'Projects'


class ProjectNoteTypesAPIClient(AutotaskPicklistAPIClient):
    API_ENTITY = 'ProjectNotes'


class TicketChecklistItemsAPIClient(ChildAPIMixin, AutotaskAPIClient):
    API = 'TicketChecklistItems'
    PARENT_API = 'Tickets'
    CHILD_API = 'ChecklistItems'

    def get(self, next_url, *args, **kwargs):
        return self.fetch_resource(next_url, *args, **kwargs)

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


class AttachmentInfoAPIClient(AutotaskAPIClient):
    API = 'AttachmentInfo'

    def document_download(self, object_id, document_id, record_type):
        ENDPOINT_DOCUMENTS_DOWNLOAD = f'{record_type}/{object_id}' \
                                      f'/Attachments/{document_id}'

        endpoint = f'{self.api_base_url}/{ENDPOINT_DOCUMENTS_DOWNLOAD}'

        try:
            logger.debug('Making GET request to {}'.format(endpoint))
            response = requests.get(
                endpoint,
                timeout=self.timeout,
                headers=self.get_headers('GET'),
            )
        except requests.RequestException as e:
            logger.error('Request failed: GET {}: {}'.format(endpoint, e))
            raise AutotaskAPIError('{}'.format(e))

        if 200 <= response.status_code < 300:
            if response.json().get('items'):
                response = response.json().get('items')[0]

            return response
        else:
            self._log_failed(response)
            return None

    def upload_attachments(self, object_id, file, recordType):
        ENDPOINT_DOCUMENTS = f'{recordType}/{object_id}/Attachments'
        endpoint_url = f'{self.api_base_url}/{ENDPOINT_DOCUMENTS}'

        file_name, file_content = file['file']
        file_data = encode_file_to_base64(file_content)

        body = {
            "id": 0,
            "attachmentType": "FILE_ATTACHMENT",
            "fullPath": file_name,
            "publish": 1,
            "title": file_name,
            "data": file_data
        }

        response = self.request('POST', endpoint_url, body)

        return response

    def get_attachment(self, object_id, document_id, record_type):
        return self.document_download(object_id, document_id, record_type)

    def count(self, *args, **kwargs):
        kwargs['record_count'] = True

        return self.fetch_resource(*args, **kwargs)

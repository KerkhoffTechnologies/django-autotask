import json
import logging

import requests
from django.conf import settings
from retrying import retry
from django.core.cache import cache

from djautotask.utils import DjautotaskSettings

RETRY_WAIT_EXPONENTIAL_MULTAPPLIER = 1000  # Initial number of milliseconds to
# wait before retrying a request.
RETRY_WAIT_EXPONENTIAL_MAX = 10000  # Maximum number of milliseconds to wait

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


class AutotaskAPIClient(object):
    API = None
    GET_QUERY = 'query?search='
    POST_QUERY = 'query'
    QUERYSTR = None

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
        self.api_base_url = None
        self.build_api_base_url()

    def _endpoint(self):
        return '{0}{1}{2}'.format(self.api_base_url,
                                  self.GET_QUERY,
                                  self.QUERYSTR)

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

    def build_api_base_url(self):
        self.api_base_url = '{0}v{1}/{2}/'.format(
            self.server_url,
            settings.AUTOTASK_CREDENTIALS['rest_api_version'],
            self.API,
        )

    def get_headers(self):
        headers = {'Content-Type': 'application/json'}

        if self.username:
            headers['UserName'] = self.username
        if self.password:
            headers['Secret'] = self.password
        if self.integration_code:
            headers['ApiIntegrationCode'] = self.integration_code

        return headers

    def build_query_string(self, **kwargs):
        filter_array = self._build_filter(**kwargs)
        query_obj = {'filter': filter_array}
        self.QUERYSTR = json.dumps(query_obj)

    def _build_filter(self, **kwargs):
        filter_array = []
        if 'conditions' in kwargs:
            for condition in kwargs['conditions']:
                filter_obj = self._build_filter_obj(*condition)
                filter_array.append(filter_obj)
        return filter_array

    def _build_filter_obj(self, field, value, op='eq'):
        filter_obj = {"op": op, "field": field, "value": value}
        return filter_obj

    def fetch_resource(self, next_url=None, retry_counter=None, *args,
                       **kwargs):
        """
        Issue a POST request to the specified REST endpoint.

        retry_counter is a dict in the form {'count': 0} that is passed in
        to verify the number of attempts that were made.
        """
        @retry(stop_max_attempt_number=self.request_settings['max_attempts'],
               wait_exponential_multiplier=RETRY_WAIT_EXPONENTIAL_MULTAPPLIER,
               wait_exponential_max=RETRY_WAIT_EXPONENTIAL_MAX,
               retry_on_exception=retry_if_api_error)
        def _fetch_resource(endpoint, retry_counter=None, **kwargs):
            if not retry_counter:
                retry_counter = {'count': 0}
            retry_counter['count'] += 1

            try:
                logger.debug('Making GET request to {}'.format(endpoint))
                response = requests.get(
                    endpoint,
                    timeout=self.timeout,
                    headers=self.get_headers(),
                )

            except requests.RequestException as e:
                logger.error('Request failed: GET {}: {}'.format(endpoint, e))
                raise AutotaskAPIError('{}'.format(e))

            if 200 <= response.status_code < 300:
                return response.json()
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

        # QUERYSTR should be the same through the all the requests of any page
        if not self.QUERYSTR:
            self.build_query_string(**kwargs)

        if next_url:
            endpoint = next_url
        else:
            endpoint = self._endpoint()

        return _fetch_resource(endpoint, retry_counter=retry_counter, **kwargs)

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
            raise AutotaskAPIServerError(
                self._prepare_error_response(response))
        else:
            self._log_failed(response)
            raise AutotaskAPIError(response)


class ContactsAPIClient(AutotaskAPIClient):
    API = 'contacts'

    def get_contacts(self, next_url, *args, **kwargs):
        return self.fetch_resource(next_url, *args, **kwargs)

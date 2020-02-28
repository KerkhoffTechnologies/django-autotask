import logging
import requests
from requests.exceptions import RequestException
from io import BytesIO
import suds.transport as transport
from atws.wrapper import AutotaskAPIException, ResponseQuery, Wrapper
from atws import wrapper, connection, Query

from django.conf import settings
from djautotask.utils import DjautotaskSettings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class AtwsTransportError(Exception):
    """
    Raise this to indicate exceptions when attempting to get autotask URLs.
    Atws captures requests.RequestException and re-raises them as
    transport.TransportError
    """
    pass


def parse_autotaskprocessexception(e):
    """
    AutotaskProcessException could have any exception wrapped inside of it,
    so handle as an AutotaskAPIException if a response attr is present,
    or handle as we would a regular exception we don't know about.
    """
    response = getattr(e.exception, 'response', None)
    if response:
        msg = str(response.errors)
    else:
        msg = str(e.args[0])
    return msg


def parse_autotaskapiexception(e):
    return ', '.join(get_errors(e.response.errors))


def get_errors(response):
    errors = []
    try:
        for item in response:
            error = item.get('errors')
            message = error[0].get('message')
            errors.append(str(message))
    except (IndexError, TypeError, AttributeError, KeyError):
        # AutotaskAPIException, has given us something unexpected, log
        # it and we can handle this new case.
        logger.exception(str(response))
        errors.append("An unknown Autotask API error.")

    return errors


def init_api_connection(**kwargs):
    client_options = kwargs.setdefault('client_options', {})

    kwargs['apiversion'] = settings.AUTOTASK_CREDENTIALS['api_version']
    kwargs['integrationcode'] = \
        settings.AUTOTASK_CREDENTIALS['integration_code']
    kwargs['username'] = settings.AUTOTASK_CREDENTIALS['username']

    client_options['transport'] = AutotaskRequestsTransport()

    client_options['url'] = get_connection_url(**kwargs)

    return Wrapper(**kwargs)


def get_cached_url(cache_key):
    return cache.get(cache_key)


def get_connection_url(**kwargs):
    cache_key = 'zone_wsdl_url'

    logger.debug('Fetching Autotask wsdl url from cache.')
    wsdl_url_from_cache = get_cached_url(cache_key)
    logger.debug(
        'Cached Autotask {} was: {}'.format(
            cache_key,
            wsdl_url_from_cache
        )
    )

    if not wsdl_url_from_cache:
        try:
            url = connection.get_connection_url(**kwargs)
            cache.set(cache_key, url)
        except transport.TransportError as e:
            raise AtwsTransportError(
                        'Failed to get webservices URL: {}'.format(e)
            )
    else:
        url = wsdl_url_from_cache

    return url


def get_web_url():
    cache_key = 'zone_web_url'
    web_url_from_cache = get_cached_url(cache_key)

    if not web_url_from_cache:
        try:
            url = connection.get_zone_info(
                settings.AUTOTASK_CREDENTIALS['username'],
                settings.AUTOTASK_CREDENTIALS['api_version']
            )['WebUrl']
            cache.set(cache_key, url, timeout=None)
        except transport.TransportError as e:
            raise AtwsTransportError('Failed to get web URL: {}'.format(e))
    else:
        url = web_url_from_cache

    return url


class AutotaskRequestsTransport(transport.Transport):
    # Adapted from atws.connection.RequestsTransport so that we can set
    # our own request settings.

    def __init__(self):
        transport.Transport.__init__(self)

        self.request_settings = DjautotaskSettings().get_settings()
        self.session = requests.Session()
        self.timeout = self.request_settings.get('timeout')
        self.max_attempts = self.request_settings.get('max_attempts')

        self.session.auth = (
            settings.AUTOTASK_CREDENTIALS['username'],
            settings.AUTOTASK_CREDENTIALS['password']
        )
        self.session.mount(
            'https://',
            requests.adapters.HTTPAdapter(
                max_retries=self.request_settings.get('max_attempts'))
        )

    def format_error_message(self, error):
        response = ResponseQuery(wrapper.Wrapper)
        response.add_error(str(error))

        return response

    def open(self, request):
        for attempt in range(1, self.max_attempts + 1):
            try:
                resp = self.session.get(request.url, timeout=self.timeout)
                break
            except RequestException as e:
                if attempt == self.max_attempts:
                    response = self.format_error_message(e)
                    raise AutotaskAPIException(response)
                continue

        return BytesIO(resp.content)

    def send(self, request):
        for attempt in range(1, self.max_attempts + 1):
            try:
                resp = self.session.post(
                    request.url,
                    data=request.message,
                    headers=request.headers,
                    timeout=self.timeout
                )
                break
            except RequestException as e:
                if attempt == self.max_attempts:
                    response = self.format_error_message(e)
                    raise AutotaskAPIException(response)
                continue

        return transport.Reply(
            resp.status_code,
            resp.headers,
            resp.content,
        )


def fetch_object(entity, object_id, at):
    """
    Fetch the give entity from the Autotask.
    """
    query = Query(entity)
    query.WHERE('id', query.Equals, object_id)

    return at.query(query).fetch_one()


def update_object(entity_type, object_id, updated_fields):
    """
    Send updates to Autotask. We need to query for the
    object first, then alter it and execute it.
    https://atws.readthedocs.io/usage.html#querying-for-entities

    This is because we can not create a valid (enough) object to update
    to autotask unless we sync EVERY non-readonly field. If you submit
    the object with no values supplied for the readonly fields,
    Autotask will null them out.
    """
    at = init_api_connection()
    instance = fetch_object(entity_type, object_id, at)

    for key, value in updated_fields.items():
        setattr(instance, key, value)

    return at.update([instance]).fetch_one()


def create_object(entity_type, entity_fields):
    """
    Make a request to Autotask to create the given Autotask entity.
    Returns the created object from the API.
    https://atws.readthedocs.io/usage.html#creating-entities
    """
    at = init_api_connection()
    entity_object = at.new(entity_type)

    for key, value in entity_fields.items():
        setattr(entity_object, key, value)

    return at.create(entity_object).fetch_one()


def update_assigned_resource(at_object, resource, role):
    entity = at_object.__class__.__name__
    query = Query(entity)
    query.WHERE('id', query.Equals, at_object.id)
    at = init_api_connection()

    t = at.query(query).fetch_one()
    t.AssignedResourceID = resource.id if resource else None
    t.AssignedResourceRoleID = role.id if role else None

    # Fetch one executes the update and returns the created object.
    return at.update([t]).fetch_one()

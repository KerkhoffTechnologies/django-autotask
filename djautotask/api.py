import requests
import logging
from requests.exceptions import ConnectTimeout, Timeout, ReadTimeout, SSLError
from io import BytesIO
import suds.transport as transport
from atws.wrapper import AutotaskAPIException, AutotaskProcessException, \
    ResponseQuery, Wrapper
from atws import wrapper, connection, Query
from atws.helpers import get_highest_id, query_result_count

from django.conf import settings
from djautotask.utils import DjautotaskSettings

logger = logging.getLogger(__name__)


class AutotaskAPIWrapper(Wrapper):
    """
    We override some methods from the atws.Wrapper to control when
    a query requires another call to the API.
    """
    def _query(self, query, response, **kwargs):

        finished = False
        while not finished:
            try:
                xml = query.get_query_xml()
            except AttributeError:
                xml = query
            try:
                result = self.client.service.query(xml)
                logger.info('Fetched {} {} records.'.format(
                    response.response_count, query.entity_type))

            except Exception as e:
                raise AutotaskProcessException(e, response)
            else:
                for entity in response.add_result(result, query):
                    yield entity

            if self.query_requires_another_call(result, query):
                highest_id = get_highest_id(result, query.minimum_id_field)
                query.set_minimum_id(highest_id)
                logger.info(
                    '{} query requires another call.'.format(query.entity_type)
                )
            else:
                finished = True

        if not kwargs.get('queries', False):
            response.raise_or_return_entities()

    def query_requires_another_call(self, result, query):
        request_settings = DjautotaskSettings().get_settings()
        batch_size = request_settings.get('batch_size')

        if not query.get_all_entities:
            return False
        try:
            query.get_query_xml()
        except AttributeError:
            return False

        if query_result_count(result) == batch_size:
            return True

        return False


def init_api_connection(**kwargs):
    client_options = kwargs.setdefault('client_options', {})

    kwargs['apiversion'] = settings.AUTOTASK_CREDENTIALS['api_version']
    kwargs['integrationcode'] = \
        settings.AUTOTASK_CREDENTIALS['integration_code']
    kwargs['url'] = settings.AUTOTASK_CREDENTIALS['url']

    client_options['transport'] = AutotaskRequestsTransport()

    url = connection.get_connection_url(**kwargs)
    client_options['url'] = url

    return AutotaskAPIWrapper(**kwargs)


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
            except (SSLError, ConnectTimeout, Timeout, ReadTimeout) as e:
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
                    timeout=self.max_attempts
                )
                break
            except (SSLError, Timeout) as e:
                if attempt == self.max_attempts:
                    response = self.format_error_message(e)
                    raise AutotaskAPIException(response)
                continue

        return transport.Reply(
            resp.status_code,
            resp.headers,
            resp.content,
        )


def update_ticket(ticket, status):
    # We need to query for the object first, then alter it and execute it.
    # https://atws.readthedocs.io/usage.html#querying-for-entities

    # This is because we can not create a valid (enough) object to update
    # to autotask unless we sync EVERY non-readonly field. If you submit the
    # object with no values supplied for the readonly fields, autotask will
    # null them out.
    query = Query('Ticket')
    query.WHERE('id', query.Equals, ticket.id)
    at = init_api_connection()

    t = at.query(query).fetch_one()
    t.Status = status.id

    # Fetch one executes the update and returns the created object.
    return at.update([t]).fetch_one()

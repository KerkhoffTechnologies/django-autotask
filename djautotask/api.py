import requests
from requests.exceptions import ConnectTimeout, Timeout, ReadTimeout, SSLError
from io import BytesIO
import suds.transport as transport
from atws.wrapper import AutotaskAPIException, ResponseQuery
from atws import wrapper, connection

from django.conf import settings
from djautotask.utils import DjautotaskSettings


def init_api_connection(**kwargs):
    client_options = kwargs.setdefault('client_options', {})

    kwargs['apiversion'] = settings.AUTOTASK_CREDENTIALS['api_version']
    kwargs['integrationcode'] = \
        settings.AUTOTASK_CREDENTIALS['integration_code']
    kwargs['url'] = settings.AUTOTASK_CREDENTIALS['url']

    client_options['transport'] = AutotaskRequestsTransport()

    url = connection.get_connection_url(**kwargs)
    client_options['url'] = url

    return wrapper.Wrapper(**kwargs)


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

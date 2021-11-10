import responses
import requests

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from . import mocks as mk

from .. import api
from ..api import AutotaskAPIError, AutotaskAPIClientError, \
    ApiConditionList
from ..api import ApiCondition as A


class TestApiConditionList(TestCase):

    def setUp(self):
        self.conditions = ApiConditionList()

    def test_build_query_string_single_get(self):
        c = A(op='eq', field='isActive', value='true')
        self.conditions.add(c)
        endpoint, filters = self.conditions.build_query()
        self.assertEqual(
            endpoint,
            'query?search={"filter": [{"op": "eq", "field": "isActive", '
            '"value": "true"}]}'
        )
        self.assertEqual(filters, None)

    def test_build_query_string_multiple_post(self):
        test_datetime = timezone.datetime(2019, 6, 22, 2, 0, 0,
                                          tzinfo=timezone.utc)

        c = A(
            A(op='eq', field='isActive', value='true'),
            A(
                field='lastActivityDate',
                value=test_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                op='gt'
            ),
            op='and'
        )

        self.conditions.add(c)
        endpoint, filters = self.conditions.build_query(method="post")
        str_built = '{"filter": [{"op": "and", "items": [{"op": "eq", ' \
                    '"field": "isActive", "value": "true"}, {"op": "gt", ' \
                    '"field": "lastActivityDate", "value": ' \
                    '"2019-06-22T02:00:00.000000Z"}]}]}'
        self.assertEqual(endpoint, 'query')
        self.assertEqual(filters, str_built)


class TestAutotaskAPIClient(TestCase):
    API_URL = 'https://localhost/'

    def setUp(self):
        mk.init_zone_info_connection(return_value={
            'url': self.API_URL,
            'webUrl': self.API_URL,
        })
        self.client = api.ContactsAPIClient()  # Must use a real client as
        # AutotaskAPIClient is effectively abstract

    @responses.activate
    def test_request(self):
        endpoint = 'http://example.com/'
        response = 'ok'
        responses.add(responses.GET, endpoint, json=response, status=200)

        result = self.client.request('get', endpoint, None)
        self.assertEqual(result, response)

    @responses.activate
    def test_request_failure(self):
        endpoint = 'http://example.com/'
        responses.add(
            responses.GET, endpoint, body=requests.RequestException()
        )

        with self.assertRaises(AutotaskAPIError):
            self.client.request('get', endpoint, None)

    @responses.activate
    def test_request_400(self):
        endpoint = 'http://example.com/'
        response = {'error': 'this is bad'}
        responses.add(responses.GET, endpoint, json=response, status=400)

        with self.assertRaises(AutotaskAPIError):
            self.client.request('get', endpoint, None)


class TestFetchAPIUrl(TestCase):
    API_URL = 'https://localhost/'

    def test_fetch_api_url_added_to_cache(self):
        """
        API url should be fetched to the cache after request,
        when zone info is not found in the cache
        """
        cache.clear()
        self.assertIsNone(api.get_cached_url('url'))
        mk.init_zone_info_connection(return_value={
            'url': self.API_URL,
            'webUrl': self.API_URL,
        })
        api.ContactsAPIClient()
        self.assertIsNotNone(api.get_cached_url('url'))

    def test_fetch_api_url_from_warm_cache(self):
        """
        Request shouldn't be tried, when zone info is found in the cache
        """
        # get api url from cache during __init__
        cache.set('zone_url', 'some api url')
        mk.init_zone_info_connection(return_value={
            'url': "some NEW api url",
            'webUrl': "some NEW api url",
        })
        api.ContactsAPIClient()
        self.assertEqual(api.get_cached_url('url'), 'some api url')

    def test_get_specific_api_connection_url(self):
        mk.init_zone_info_connection(return_value={
            'url': self.API_URL,
            'webUrl': self.API_URL,
        })
        client = api.ContactsAPIClient(
            server_url='https://specific-api-url.autotask.net'
        )
        self.assertEqual(
            client.server_url,
            'https://specific-api-url.autotask.net'
        )


class TestAPISettings(TestCase):
    API_URL = 'https://localhost/'

    def setUp(self):
        mk.init_zone_info_connection(return_value={
            'url': self.API_URL,
            'webUrl': self.API_URL,
        })

    def test_default_timeout(self):
        client = api.ContactsAPIClient()
        self.assertEqual(client.timeout, 30.0)

    def test_dynamic_batch_size(self):
        method_name = 'djautotask.utils.DjautotaskSettings.get_settings'
        request_settings = {
            'batch_size': 10,
            'timeout': 10.0,
        }
        _, _patch = mk.create_mock_call(method_name, request_settings)
        client = api.ContactsAPIClient()

        self.assertEqual(client.timeout,
                         request_settings['timeout'])
        _patch.stop()

    def test_retry_attempts(self):
        with self.assertRaises(AutotaskAPIError):
            retry_counter = {'count': 0}
            client = api.ContactsAPIClient()
            client.fetch_resource('http://localhost/some-bad-url',
                                  retry_counter=retry_counter)
            self.assertEqual(retry_counter['count'],
                             client.request_settings['max_attempts'])

    @responses.activate
    def test_no_retry_attempts_in_400_range(self):
        client = api.ContactsAPIClient()
        endpoint = "{}{}".format(client.get_api_url(),
                                 'query?search={"filter": []}')

        tested_status_codes = []
        http_400_range = list(range(400, 499))

        # We do actually want to retry 401, as that indicates the
        # zone information may have changed
        http_400_range.pop(1)

        for status_code in http_400_range:

            retry_counter = {'count': 0}
            try:
                mk.get(endpoint, {}, status=status_code)
                client.fetch_resource(None, retry_counter=retry_counter)
            except AutotaskAPIClientError:
                self.assertEqual(retry_counter['count'], 1)
                tested_status_codes.append(status_code)

        self.assertEqual(tested_status_codes, http_400_range)

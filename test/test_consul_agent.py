#!/usr/bin/env python
import mock
import unittest
import sys
import json
import os
from urllib.error import HTTPError
from urllib.error import URLError
sys.path.insert(0, os.path.dirname(__file__))
sys.modules['collectd'] = mock.Mock()
import consul_health_plugin # noqa
from consul_health_plugin import ConsulAgent # noqa


class MockHTTPSHandler(object):

    def __init__(self, ca_cert, client_cert, client_key):
        self.ca_cert = ca_cert
        self.client_cert = client_cert
        self.client_key = client_key


def sample_response(path):

    dir_path = os.path.dirname(os.path.realpath(__file__))
    file = dir_path + '/resources' + path
    with open(file, 'r') as data:
        return json.load(data)


class ConsulAgentTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.base_url = 'http://example.com:8888/v1'
        self.api_host = 'example.com'
        self.api_port = '8888'
        self.api_protocol = 'http'
        self.acl_token = 'acl_token'
        self.ssl_certs = {'ca_cert': None,
                          'client_cert': None,
                          'client_key': None}
        self.agent = ConsulAgent(self.api_host, self.api_port,
                                 self.api_protocol, self.acl_token,
                                 self.ssl_certs)
        self.agent.config = sample_response('/agent/self')

    @mock.patch('urllib.request.build_opener')
    def test_return_json_on_ok(self, mock_urllib_opener):

        mock_response = mock.Mock()
        mock_response.code = 200
        mock_response.read.return_value = '{"foo": "bar", "bat": "baz"}'

        mock_urllib_opener().open.return_value = mock_response

        url = 'http://example.com:8500'
        actual_response = self.agent._send_request(url)
        expected_response = {"foo": "bar", "bat": "baz"}

        expected_header = [('X-Consul-Token', self.agent.acl_token)]
        self.assertEqual(mock_urllib_opener.return_value.addheaders,
                         expected_header)
        mock_urllib_opener().open.assert_called_with(url)

        self.assertDictEqual(expected_response, actual_response)

    @mock.patch('urllib.request.build_opener')
    def test_return_none_on_exception(self, mock_urllib_opener):

        mock_urllib_opener.side_effect = HTTPError(*[None] * 5)
        self.assertIsNone(self.agent._send_request('http://example.com:8500'))

        mock_urllib_opener.side_effect = URLError('Mock URLError')
        self.assertIsNone(self.agent._send_request('http://exampl.com:8500'))

    @mock.patch('consul_health_plugin.ConsulAgent._send_request')
    def test_get_local_config(self, mock_send_request):
        expected_url = '{0}/agent/self'.format(self.base_url)
        self.agent.get_local_config()
        mock_send_request.assert_called_with(expected_url)

    @mock.patch('consul_health_plugin.ConsulAgent._send_request')
    def test_get_health_checks(self, mock_send_request):
        node = 'mhost1.dummy.net'
        expected_url = '{0}/health/node/{1}'.format(self.base_url, node)
        self.agent.get_health_checks(node)
        mock_send_request.assert_called_with(expected_url)

    @mock.patch('consul_health_plugin.ConsulAgent.get_health_checks',
                return_value=sample_response('/health/node/mhost1.dummy.net'))
    def test_get_health_check_stats(self, mock_call):
        expected_response = {'service': {
                                 'leftpad': {'passing': 1,
                                             'warning': 0,
                                             'critical': 1},
                                 'devnull': {'passing': 0,
                                             'warning': 1,
                                             'critical': 0}
                             },
                             'node': {'passing': 1,
                                      'warning': 0,
                                      'critical': 0}}

        actual_response = self.agent.get_health_check_stats()
        self.assertEqual(expected_response, actual_response)

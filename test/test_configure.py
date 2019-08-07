#!/usr/bin/env python
import mock
import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.modules['collectd'] = mock.MagicMock()
import consul_health_plugin # noqa


class TestConfiure(unittest.TestCase):

    @mock.patch('consul_health_plugin.ConsulPlugin')
    def test_default_config(self, mock_plugin):
        mock_conf = mock.Mock()
        mock_conf.children = []

        expected_conf = {'api_host': 'localhost',
                         'api_port': 8500,
                         'api_protocol': 'http',
                         'acl_token': None,
                         'ssl_certs': {'ca_cert': None, 'client_cert': None,
                                       'client_key': None},
                         'debug': False}
        consul_health_plugin.configure_callback(mock_conf)
        args, kwargs = mock_plugin.call_args
        for k, v in args[0].items():
            self.assertIn(k, expected_conf)
            self.assertEqual(v, expected_conf[k])

    @mock.patch('consul_health_plugin.ConsulPlugin')
    def test_all_config(self, mock_plugin):
        mock_plugin.read = mock.MagicMock()
        mock_plugin.shutdown = mock.MagicMock()

        mock_conf = mock.Mock()

        expected_host = '10.2.5.60'
        mock_host = _build_mock_config_child('ApiHost', expected_host)

        expected_port = 8080
        mock_port = _build_mock_config_child('ApiPort', str(expected_port))

        expected_protocol = 'https'
        mock_protocol = _build_mock_config_child('ApiProtocol',
                                                 expected_protocol)

        expected_acl_token = 'acl_token'
        mock_acl_token = _build_mock_config_child('AclToken',
                                                  expected_acl_token)

        expected_ca_cert = '/path/to/ca/cert'
        mock_ca_cert = _build_mock_config_child('CaCertificate',
                                                expected_ca_cert)

        expected_client_cert = '/path/to/clien/cert'
        mock_client_cert = _build_mock_config_child('ClientCertificate',
                                                    expected_client_cert)

        expected_client_key = '/path/to/client/key'
        mock_client_key = _build_mock_config_child('ClientKey',
                                                   expected_client_key)

        expected_ssl_certs = {'ca_cert': expected_ca_cert,
                              'client_cert': expected_client_cert,
                              'client_key': expected_client_key}

        expected_debug = False
        mock_debug = _build_mock_config_child('Debug', expected_debug)

        mock_conf.children = [mock_host,
                              mock_port,
                              mock_protocol,
                              mock_acl_token,
                              mock_ca_cert,
                              mock_client_cert,
                              mock_client_key,
                              mock_debug]

        expected_conf = {'api_host': expected_host,
                         'api_port': expected_port,
                         'api_protocol': expected_protocol,
                         'acl_token': expected_acl_token,
                         'ssl_certs': expected_ssl_certs,
                         'debug': expected_debug}

        consul_health_plugin.configure_callback(mock_conf)
        args, kwargs = mock_plugin.call_args
        for k, v in args[0].items():
            self.assertEqual(v, expected_conf[k])

        consul_health_plugin.collectd.register_read.assert_called_once()
        consul_health_plugin.collectd.register_read.assert_called_with(
            mock_plugin().read,
            name='consul-health.{}:{}'.format(expected_host,
                                              expected_port))


def _build_mock_config_child(key, value):
    mock_config_child = mock.Mock()
    mock_config_child.key = key
    mock_config_child.values = [value]
    return mock_config_child

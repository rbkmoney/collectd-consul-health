#!/usr/bin/env python
import os
import sys
import json
import unittest
from mock import Mock, MagicMock, patch
import re
import logging
sys.path.insert(0, os.path.dirname(__file__))
# Mock out the collectd module
sys.modules['collectd'] = Mock()
import consul_health_plugin


class MockMetricSink(object):
    def __init__(self):
        self.captured_records = []

    def emit(self, metric_record):
        self.captured_records.append(metric_record)


class TestConsulPlugin(unittest.TestCase):

    @patch('consul_health_plugin.MetricSink')
    def setUp(self, mock_sink):
        self.maxDiff = None
        mock_consul_agent = self._build_mock_consul_agent()
        mock_sink.side_effect = MockMetricSink
        self.plugin_conf = {'api_host': 'example',
                            'api_port': 8500,
                            'api_protocol': 'http',
                            'acl_token': None,
                            'ssl_certs': {'ca_cert': None,
                                          'client_cert': None,
                                          'client_key': None},
                            'debug': False
                            }
        with patch('consul_health_plugin.ConsulAgent') as m_agent:
            m_agent.return_value = mock_consul_agent
            self.plugin = consul_health_plugin.ConsulPlugin(self.plugin_conf)

    def test_fetch_health_checks(self):

        expected_records = []

        expected_records.append(consul_health_plugin.MetricRecord(
            'service.leftpad.passing',
            'gauge',
            1))
        expected_records.append(consul_health_plugin.MetricRecord(
            'service.leftpad.warning',
            'gauge',
            0))
        expected_records.append(consul_health_plugin.MetricRecord(
            'service.leftpad.critical',
            'gauge',
            1))

        expected_records.append(consul_health_plugin.MetricRecord(
            'service.devnull.passing',
            'gauge',
            0))
        expected_records.append(consul_health_plugin.MetricRecord(
            'service.devnull.warning',
            'gauge',
            1))
        expected_records.append(consul_health_plugin.MetricRecord(
            'service.devnull.critical',
            'gauge',
            0))

        expected_records.append(consul_health_plugin.MetricRecord(
            'node.passing',
            'gauge',
            1))
        expected_records.append(consul_health_plugin.MetricRecord(
            'node.warning',
            'gauge',
            0))
        expected_records.append(consul_health_plugin.MetricRecord(
            'node.critical',
            'gauge',
            0))

        actual_records = self.plugin._fetch_health_checks()

        self.assertEqual(len(expected_records), len(actual_records))

        for (idx, record) in enumerate(actual_records):
            self._validate_single_record(expected_records[idx], record)

    def _sample_response(self, path):

        dir_name = os.path.dirname(os.path.realpath(__file__))
        file = dir_name + '/resources' + path
        with open(file, 'r') as data:
            return json.load(data)

    def _build_mock_consul_agent(self):

        mock_agent = Mock()
        api_host = 'example'
        api_port = 8500
        api_protocol = 'http'
        acl_token = None
        ssl_certs = {'ca_cert': None,
                     'client_cert': None,
                     'client_key': None}
        agent = consul_health_plugin.ConsulAgent(api_host, api_port, api_protocol,
                                                 acl_token, ssl_certs)
        agent.config = self._sample_response('/agent/self')

        mock_agent.config = self._sample_response('/agent/self')
        mock_agent.update_local_config = MagicMock()

        with patch('consul_health_plugin.ConsulAgent.get_health_checks') as mcall:
            mcall.return_value = self._sample_response('/health/node/mhost1.dummy.net')
            h_map = agent.get_health_check_stats()
            mock_agent.get_health_check_stats = MagicMock(return_value=h_map)

        return mock_agent

    def _validate_single_record(self, expected_record, actual_record):
        self.assertIsNotNone(actual_record)
        self.assertEqual(expected_record.name, actual_record.name)
        self.assertEqual(expected_record.type, actual_record.type)
        self.assertEqual(expected_record.value, actual_record.value)
        self.assertIsNotNone(actual_record.timestamp)

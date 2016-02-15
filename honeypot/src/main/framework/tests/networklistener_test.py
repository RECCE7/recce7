__author__ = 'Jesse Nelson <jnels1242012@gmail.com>, ' \
             'Randy Sorensen <sorensra@msudenver.edu>'

import unittest
import socket
from networklistener import NetworkListener
from frmwork import Framework
from unittest.mock import patch


def make_mock_config(port, module):
    return {
        'port': port,
        'module': module,
        'table': 'test',
        'enabled': 'Yes',
        'tableColumns': [[1, 'INTEGER', 'someNumber'], [2, 'TEXT', 'someText']]
    }


class NetworkListenerTest(unittest.TestCase):
    def setUp(self):
        pass

    @patch('networklistener.NetworkListener.start_listening')
    def test_plugins_enabled(self, test_start_listening):
        mock_config = make_mock_config(8082, 'HTTPPlugin')
        listener = NetworkListener(mock_config, None)
        listener.start()
        while listener.connection_count == 0:
            pass
        listener.stop()
        self.assertTrue(test_start_listening.called)

    def test_connection_count(self):
        mock_config = make_mock_config(8082, 'HTTPPlugin')
        listener = NetworkListener(mock_config, None)
        self.assertEqual(0, listener.connection_count)
        listener.connection_count = 5
        self.assertEqual(5, listener.connection_count)

    @patch('networklistener.socket.socket.accept',
           return_value=(socket.socket(), '0.0.0.0'))
    @patch.object(Framework, 'spawn')
    @patch('frmwork.Framework.spawn')
    def test_start_listening(self, mock_accept, mock_framework, mock_spawn):
        mock_config = make_mock_config(8082, 'HTTPPlugin')
        listener = NetworkListener(mock_config, mock_framework())
        listener.start_listening(socket.socket())
        self.assertTrue(mock_accept.called)
        self.assertTrue(mock_spawn.called)

    @patch('networklistener.socket.socket.accept',
           return_value=(socket.socket(), '0.0.0.0'))
    @patch.object(Framework, 'spawn')
    def test_start_listening_exception(self, mock_accept, mock_framework):
        mock_config = make_mock_config(8082, 'HTTPPlugin')
        listener = NetworkListener(mock_config, mock_framework)
        listener.start_listening(None)
        self.assertTrue(mock_accept.called)

    def tearDown(self):
        pass

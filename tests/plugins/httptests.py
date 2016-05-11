import unittest
import socket

from plugins.http import HTTPPlugin


def setup_test_config(test_port, test_module, test_class):
    return {
        'port': test_port,
        'module': test_module,
        'moduleClass': test_class,
        'table': 'test',
        'enabled': 'Yes',
        'rawSocket': 'No',
        'tableColumns': [[1, 'command', 'TEXT'], [2, 'path', 'TEXT'], [3, 'headers', 'TEXT'], [4, 'body', 'TEXT']]
    }


def setup_test_sockets(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', port))
    server_socket.listen(1)
    test_socket_send = socket.socket()
    test_socket_send.connect(('', port))
    (test_socket_recv, addr) = server_socket.accept()
    server_socket.close()

    return test_socket_send, test_socket_recv


class HTTPPluginTest(unittest.TestCase):
    # Test the dictionary creation from get_entry inside the Base_Plugin
    def test_get_entry(self):
        # Test the get_entry for the http configurations
        test_client, test_server = setup_test_sockets(8083)

        plugin_test = HTTPPlugin(test_server, setup_test_config(8083, 'http', 'HTTPPlugin'), None)

        self.assertEqual(plugin_test.get_entry(), {'test': {'command': '',
                                                            'path': '',
                                                            'headers': '',
                                                            'body': ''}})

        test_server.close()
        test_client.close()

    def test_get_200(self):
        """
        Test a GET to the login page
        """
        test_client, test_server = setup_test_sockets(8083)
        plugin_test = HTTPPlugin(test_server, setup_test_config(8083, 'http', 'HTTPPlugin'), None)

        test_client.send(b'GET / HTTP/1.1\r\n'
                         b'Connection: close\r\n\r\n')

        plugin_test.handle_one_request()
        plugin_test.format_data()
        entry = plugin_test.get_entry()

        self.assertEqual(entry, {'test': {'command': 'GET',
                                          'path': '/',
                                          'headers': 'Connection: close\n\n',
                                          'body': ''}})
        self.assertEqual("200" in test_client.recv(1024).decode(), True)

        test_server.close()
        test_client.close()

    def test_get_404(self):
        """
        Test a get to a nonexistent page
        """
        test_client, test_server = setup_test_sockets(8083)
        plugin_test = HTTPPlugin(test_server, setup_test_config(8083, 'http', 'HTTPPlugin'), None)

        test_client.send(b'GET /test HTTP/1.1\r\n'
                         b'Connection: close\r\n\r\n')

        plugin_test.handle_one_request()
        plugin_test.format_data()
        entry = plugin_test.get_entry()

        self.assertEqual(entry, {'test': {'command': 'GET',
                                          'path': '/test',
                                          'headers': 'Connection: close\n\n',
                                          'body': ''}})

        self.assertEqual("404" in test_client.recv(1024).decode(), True)

        test_server.close()
        test_client.close()

    def test_head_200(self):
        """
        Test a HEAD request to the login page
        """
        test_client, test_server = setup_test_sockets(8083)
        plugin_test = HTTPPlugin(test_server, setup_test_config(8083, 'http', 'HTTPPlugin'), None)

        test_client.send(b'HEAD / HTTP/1.1\r\n'
                         b'Connection: close\r\n\r\n')

        plugin_test.handle_one_request()
        plugin_test.format_data()
        entry = plugin_test.get_entry()

        self.assertEqual(entry, {'test': {'command': 'HEAD',
                                          'path': '/',
                                          'headers': 'Connection: close\n\n',
                                          'body': ''}})
        self.assertEqual("200" in test_client.recv(1024).decode(), True)

        test_server.close()
        test_client.close()

    def test_head_404(self):
        """
        Test a HEAD request to a bad page
        """
        test_client, test_server = setup_test_sockets(8083)
        plugin_test = HTTPPlugin(test_server, setup_test_config(8083, 'http', 'HTTPPlugin'), None)

        test_client.send(b'HEAD /test HTTP/1.1\r\n'
                         b'Connection: close\r\n\r\n')

        plugin_test.handle_one_request()
        plugin_test.format_data()
        entry = plugin_test.get_entry()

        self.assertEqual(entry, {'test': {'command': 'HEAD',
                                          'path': '/test',
                                          'headers': 'Connection: close\n\n',
                                          'body': ''}})
        self.assertEqual("404" in test_client.recv(1024).decode(), True)

        test_server.close()
        test_client.close()

    def test_post_200(self):
        """
        Test a POST to an empty url
        """
        test_client, test_server = setup_test_sockets(8083)
        plugin_test = HTTPPlugin(test_server, setup_test_config(8083, 'http', 'HTTPPlugin'), None)

        test_client.send(b'POST / HTTP/1.1\r\n'
                         b'Connection: close\r\n'
                         b'Content-type: text/html\r\n'
                         b'Content-length: 27\r\n'
                         b'\r\n'
                         b'username=test&password=test')

        plugin_test.handle_one_request()
        plugin_test.format_data()
        entry = plugin_test.get_entry()

        self.assertEqual(entry, {'test': {'command': 'POST',
                                          'path': '/',
                                          'headers': 'Connection: close\nContent-type: text/html\n'
                                                     'Content-length: 27\n\n',
                                          'body': 'username=test&password=test'}})
        self.assertEqual("200" in test_client.recv(1024).decode(), True)

        test_server.close()
        test_client.close()

    def test_post_403(self):
        """
        Test a POST to the login page
        """
        test_client, test_server = setup_test_sockets(8083)
        plugin_test = HTTPPlugin(test_server, setup_test_config(8083, 'http', 'HTTPPlugin'), None)

        test_client.send(b'POST /login HTTP/1.1\r\n'
                         b'Connection: close\r\n'
                         b'Content-type: text/html\r\n'
                         b'Content-length: 27\r\n'
                         b'\r\n'
                         b'username=test&password=test')

        plugin_test.handle_one_request()
        plugin_test.format_data()
        entry = plugin_test.get_entry()

        self.assertEqual(entry, {'test': {'command': 'POST',
                                          'path': '/login',
                                          'headers': 'Connection: close\nContent-type: text/html\n'
                                                     'Content-length: 27\n\n',
                                          'body': 'username=test&password=test'}})
        self.assertEqual("403" in test_client.recv(1024).decode(), True)

        test_server.close()
        test_client.close()

    def test_post_404(self):
        """
        Test a POST to a bad page
        """
        test_client, test_server = setup_test_sockets(8083)
        plugin_test = HTTPPlugin(test_server, setup_test_config(8083, 'http', 'HTTPPlugin'), None)

        test_client.send(b'POST /test HTTP/1.1\r\n'
                         b'Connection: close\r\n'
                         b'Content-type: text/html\r\n'
                         b'Content-length: 27\r\n'
                         b'\r\n'
                         b'username=test&password=test')

        plugin_test.handle_one_request()
        plugin_test.format_data()
        entry = plugin_test.get_entry()

        self.assertEqual(entry, {'test': {'command': 'POST',
                                          'path': '/test',
                                          'headers': 'Connection: close\nContent-type: text/html\n'
                                                     'Content-length: 27\n\n',
                                          'body': 'username=test&password=test'}})
        self.assertEqual("404" in test_client.recv(1024).decode(), True)

        test_server.close()
        test_client.close()

    def test_real_501(self):
        """
        Test a PUT command
        PUT, OPTIONS, DELETE, TRACE, and CONNECT should all have the same behavior.
        These commands send back a 501 error stating that the commands
        are not supported.
        """

        test_client, test_server = setup_test_sockets(8083)

        plugin_test = HTTPPlugin(test_server, setup_test_config(8083, 'http', 'HTTPPlugin'), None)

        test_client.send(b'PUT / HTTP/1.1\r\n'
                         b'Connection: close\r\n'
                         b'\r\n')

        plugin_test.handle_one_request()
        plugin_test.format_data()
        entry = plugin_test.get_entry()

        self.assertEqual(entry, {'test':
                                 {'command': 'PUT',
                                  'path': '/',
                                  'headers': 'Connection: close\n\n',
                                  'body': ''}})
        self.assertEqual("501" in test_client.recv(1024).decode(), True)

        test_server.close()
        test_client.close()

    def test_fake_501(self):
        """
        Test a bad http command
        If a command comes through that has no do_<command>
        defined it should be treated like a 501 and still
        be written to the database
        """

        test_client, test_server = setup_test_sockets(8083)

        plugin_test = HTTPPlugin(test_server, setup_test_config(8083, 'http', 'HTTPPlugin'), None)

        test_client.send(b'TEST / HTTP/1.1\r\n'
                         b'Connection: close\r\n'
                         b'\r\n')

        plugin_test.handle_one_request()
        plugin_test.format_data()
        entry = plugin_test.get_entry()

        self.assertEqual(entry, {'test': {'command': 'TEST',
                                          'path': '/',
                                          'headers': 'Connection: close\n\n',
                                          'body': ''}})
        self.assertEqual("501" in test_client.recv(1024).decode(), True)

        test_server.close()
        test_client.close()

if __name__ == '__main__':
    unittest.main()

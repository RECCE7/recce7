import unittest
import socket

from plugins.telnet import TelnetPlugin


def setup_test_config(test_port, test_module, test_class):
    return dict(port=test_port, module=test_module, moduleClass=test_class, table='test', enabled='Yes', rawSocket='No',
                tableColumns=[[1, 'input_type', 'TEXT'], [2, 'user_input', 'TEXT']])


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


class TelnetPluginTest(unittest.TestCase):
    def test_get_entry(self):
        test_client, test_server = setup_test_sockets(8023)
        plugin_test = TelnetPlugin(test_server, setup_test_config(8023, 'telnet', 'TelnetPlugin'), None)

        self.assertEqual(plugin_test.get_entry(), {'test': {'input_type': '', 'user_input': ''}})

        test_server.close()
        test_client.close()

    def test_username(self):
        test_client, test_server = setup_test_sockets(8023)
        plugin_test = TelnetPlugin(test_server, setup_test_config(8023, 'telnet', 'TelnetPlugin'), None)

        test_client.send(b'test_username\r\n')
        plugin_test.username()

        self.assertEqual(test_client.recv(1024), b'Username: ')
        self.assertEqual(plugin_test.get_entry(), {'test': {'input_type': 'username', 'user_input': 'test_username'}})

        test_server.close()
        test_client.close()

    def test_password(self):
        test_client, test_server = setup_test_sockets(8023)
        plugin_test = TelnetPlugin(test_server, setup_test_config(8023, 'telnet', 'TelnetPlugin'), None)

        test_client.send(b'test_password\r\n')
        plugin_test.password()

        self.assertEqual(test_client.recv(1024), b'Password: ')
        self.assertEqual(plugin_test.get_entry(), {'test': {'input_type': 'password', 'user_input': 'test_password'}})

        test_server.close()
        test_client.close()

    def test_help_command(self):
        test_client, test_server = setup_test_sockets(8023)
        plugin_test = TelnetPlugin(test_server, setup_test_config(8023, 'telnet', 'TelnetPlugin'), None)

        test_client.send(b'help\r\n')
        plugin_test.command()

        self.assertEqual(test_client.recv(2), b'. ')
        help = test_client.recv(1024).decode()
        self.assertEquals("options:\t" in help, True)
        self.assertEquals("options:\t\t" in help, False)
        self.assertEquals("help:" in help, True)
        self.assertEquals("echo:" in help, True)
        self.assertEquals("quit:" in help, True)
        self.assertEquals("__init__:" in help, False)

        self.assertEquals("basic list of options available to user" in help, True)
        self.assertEquals("detailed description of options" in help, True)
        self.assertEquals("prompt to echo back typing" in help, True)
        self.assertEquals("close telnet connection to server" in help, True)

        self.assertEqual(plugin_test.get_entry(), {'test': {'input_type': 'command', 'user_input': 'help'}})

        test_server.close()
        test_client.close()

    def test_options_command(self):
        test_client, test_server = setup_test_sockets(8023)
        plugin_test = TelnetPlugin(test_server, setup_test_config(8023, 'telnet', 'TelnetPlugin'), None)

        test_client.send(b'options\r\n')
        plugin_test.command()

        self.assertEqual(test_client.recv(2), b'. ')
        options = test_client.recv(1024).decode()
        self.assertEquals("options\t\t" in options, True)
        self.assertEquals("help\t\t" in options, True)
        self.assertEquals("echo\t\t" in options, True)
        self.assertEquals("quit\t\t" in options, True)
        self.assertEquals("__init__\t\t" in options, False)
        self.assertEqual(plugin_test.get_entry(), {'test': {'input_type': 'command', 'user_input': 'options'}})

        test_server.close()
        test_client.close()

    def test_quit_command(self):
        test_client, test_server = setup_test_sockets(8023)
        plugin_test = TelnetPlugin(test_server, setup_test_config(8023, 'telnet', 'TelnetPlugin'), None)

        test_client.send(b'quit\r\n')
        plugin_test.command()

        self.assertEqual(test_client.recv(2), b'. ')
        self.assertEqual(test_client.recv(1024), b'\nGoodbye\n')

        self.assertEqual(plugin_test.get_entry(), {'test': {'input_type': 'command', 'user_input': 'quit'}})

        test_server.close()
        test_client.close()

    def test_echo_arguments(self):
        test_client, test_server = setup_test_sockets(8023)
        plugin_test = TelnetPlugin(test_server, setup_test_config(8023, 'telnet', 'TelnetPlugin'), None)

        test_client.send(b'echo test test\r\n')
        plugin_test.command()

        self.assertEqual(test_client.recv(2), b'. ')
        self.assertEqual(test_client.recv(1024), b'test test\r\n')

        self.assertEqual(plugin_test.get_entry(), {'test': {'input_type': 'echo', 'user_input': 'test test'}})

        test_server.close()
        test_client.close()

    def test_echo_no_arguments(self):
        test_client, test_server = setup_test_sockets(8023)
        plugin_test = TelnetPlugin(test_server, setup_test_config(8023, 'telnet', 'TelnetPlugin'), None)

        test_client.send(b'echo\r\n')
        test_client.send(b'test test\r\n')
        plugin_test.command()

        self.assertEqual(plugin_test.get_entry(), {'test': {'input_type': 'echo', 'user_input': 'test test'}})

        test_server.close()
        test_client.close()

    def test_handle_echo(self):
        test_client, test_server = setup_test_sockets(8023)
        plugin_test = TelnetPlugin(test_server, setup_test_config(8023, 'telnet', 'TelnetPlugin'), None)

        plugin_test.echo('test test')

        self.assertEqual(plugin_test.get_entry(), {'test': {'input_type': 'echo', 'user_input': 'test test'}})

        test_server.close()
        test_client.close()

    def test_bad_command(self):
        test_client, test_server = setup_test_sockets(8023)
        plugin_test = TelnetPlugin(test_server, setup_test_config(8023, 'telnet', 'TelnetPlugin'), None)

        test_client.send(b'bad_command\r\n')
        plugin_test.command()

        self.assertEqual(test_client.recv(2), b'. ')
        self.assertEqual(test_client.recv(1024), b'%unrecognized command - type options for a list\r\n')
        self.assertEqual(plugin_test.get_entry(), {'test': {'input_type': 'command', 'user_input': 'bad_command'}})

        test_server.close()
        test_client.close()

    def test_locked_command(self):
        test_client, test_server = setup_test_sockets(8023)
        plugin_test = TelnetPlugin(test_server, setup_test_config(8023, 'telnet', 'TelnetPlugin'), None)

        test_client.send(b'__class__\r\n')
        plugin_test.command()

        self.assertEqual(test_client.recv(2), b'. ')
        self.assertEqual(test_client.recv(1024), b'%unrecognized command - type options for a list\r\n')
        self.assertEqual(plugin_test.get_entry(), {'test': {'input_type': 'command', 'user_input': '__class__'}})

        test_server.close()
        test_client.close()

    def test_runthrough(self):
        test_client, test_server = setup_test_sockets(8023)
        plugin_test = TelnetPlugin(test_server, setup_test_config(8023, 'telnet', 'TelnetPlugin'), None)
        plugin_test.start()

        test_client.send(b'test_username\r\n')
        test_client.send(b'test_password\r\n')
        test_client.send(b'quit\r\n')

        test_client.close()

    def test_multiple_quit(self):
        test_client, test_server = setup_test_sockets(8023)
        plugin_test = TelnetPlugin(test_server, setup_test_config(8023, 'telnet', 'TelnetPlugin'), None)
        plugin_test.start()

        test_client.send(b'test_username\r\n')
        test_client.send(b'test_password\r\n')
        test_client.send(b'quit;quit;quit\r\n')

        test_client.close()

if __name__ == '__main__':
    unittest.main()

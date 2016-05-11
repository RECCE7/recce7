"""
Plugin base class

Contents
- BasePlugin: Base class for all plugins.
"""

import platform
import socket
import datetime

from recon.p0fagent import P0fAgent
from threading import Thread
from uuid import uuid4


class BasePlugin(Thread):
    """

    """
    def __init__(self, _skt, config, framework):
        """

        """
        Thread.__init__(self)
        self._skt = _skt
        self._localAddress = None
        self._peerAddress = None
        self.get_addresses()
        self._config = config
        self._framework = framework
        self._session = None
        self.kill_plugin = False

    def get_addresses(self):
        try:
            self._localAddress = self._skt.getsockname()[0]
            self._peerAddress = self._skt.getpeername()[0]
        #TODO write something to database for potential scans
        except ConnectionResetError:
            self.kill_plugin = True
            self.close_descriptors()
        except OSError:
            self.kill_plugin = True
            self.close_descriptors()

    def run(self):
        """

        """
        if not self.kill_plugin:
            try:
                self.do_track()
            except OSError:
                self.kill_plugin = True
                self.close_descriptors()
                return
            except AttributeError:
                self.kill_plugin = True
                self.close_descriptors()
                return
            except UnicodeDecodeError:
                self.kill_plugin = True
                self.close_descriptors()
                return
            except ValueError:
                self.kill_plugin = True
                self.close_descriptors()
                return

        self.get_p0f_info()

        #
        # NOTE: Do NOT call self.shutdown() here! To shutdown this
        # thread, just return from this run() method.
        #
        # self.shutdown() allows the framework to force this
        # thread to shutdown; you never need to call it.
        #
        # Calling self.shutdown() from here will cause this thread
        # to join itself - this will block forever. This in turn
        # will exceed the open file limit and cause the framework
        # to die.
        #
        # So don't call that method here! Just return from this.
        #
        self._framework.plugin_stopped(self)

    def get_p0f_info(self):
        agent = P0fAgent(self._peerAddress, self._framework, self._session)
        agent.start()

    def get_entry(self):
        entry = {self.get_table_name(): {}}
        columns = self.get_table_columns()

        for i in columns:
            try:
                entry[self.get_table_name()][i] = getattr(self, i)
            except AttributeError:
                entry[self.get_table_name()][i] = ''

        return entry

    def do_save(self):
        """

        """
        entry = self.get_entry()

        entry[self.get_table_name()]['peerAddress'] = self._peerAddress
        entry[self.get_table_name()]['localAddress'] = self._localAddress
        entry[self.get_table_name()]['eventDateTime'] = datetime.datetime.now().isoformat()
        entry[self.get_table_name()]['session'] = self._session

        try:
            self._framework.insert_data(entry)
        except AttributeError:
            return

    def close_descriptors(self):
        """
        Close any files after an exception
        """

    def shutdown(self):
        """

        """
        self.kill_plugin = True

        if self._skt:
            old_skt = self._skt
            self._skt = None
            if platform.system() == 'Linux':
                old_skt.shutdown(socket.SHUT_RDWR)
                old_skt.detach()
            old_skt.close()
        else:
            print("Socket already closed for plugin thread name: " + self.name)

        try:
            self.join()
        except RuntimeError:
            return

    def do_track(self):
        """
        Implemented by the plugin writer.
        """
        pass

    def get_session(self):
        """
        Implemented by the plugin writer.
        """
        pass

    def get_plugin_port(self):
        """
        Returns the port for this plugin.
        """
        return self._config['port']

    def get_table_name(self):
        """
        Returns the database table name for this plugin.
        """
        return self._config['table']

    def get_table_columns(self):
        """
        Returns the column names for this plugin.
        """
        columns = []

        for i in self._config['tableColumns']:
            columns.append(i[1])

        return columns

    def get_uuid4(self):
        return str(uuid4())

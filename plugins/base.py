"""
Plugin base class

Contents
- BasePlugin: Base class for all plugins.
"""

import platform
import socket
import datetime
from threading import Thread
import uuid

from uuid import uuid4

class BasePlugin(Thread):
    """

    """
    def __init__(self, socket, config, framework):
        """

        """
        Thread.__init__(self)
        self._skt = socket
        self._config = config
        self._framework = framework
        self._localAddress = self._skt.getsockname()[0]
        self._peerAddress = self._skt.getpeername()[0]
        self._session = None
        self.kill_plugin = False

    def run(self):
        """

        """

        self.do_track()

        '''while self._skt and not self.kill_plugin:
            try:
                self.do_track()
            except ConnectionResetError as cre:
                error_number = cre.errno
                if error_number == 54:  # ERRNO 54 is 'connection reset by peer'
                    # Log that it is possible we are being scanned, would want to write this to the db
                    print("Maybe we are being scanned")
                    pass

        self._framework.plugin_stopped(self)'''

    def do_save(self):
        """

        """
        entry = {self.get_table_name() : {}}
        columns = self.get_table_columns()

        for i in columns:
            try:
                entry[self.get_table_name()][i] = getattr(self, i)
            except AttributeError:
                entry[self.get_table_name()][i] = 'Attribute did not exist'

        entry[self.get_table_name()]['peerAddress'] = self._peerAddress
        entry[self.get_table_name()]['localAddress'] = self._localAddress
        entry[self.get_table_name()]['eventDateTime'] = datetime.datetime.now().isoformat()
        entry[self.get_table_name()]['session'] = self._session

        self._framework.insert_data(entry)

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

        self.join()

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
        return str(uuid.uuid4())

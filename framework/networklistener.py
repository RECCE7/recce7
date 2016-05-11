################################################################################
#                                                                              #
#                           GNU Public License v3.0                            #
#                                                                              #
################################################################################
#   HunnyPotR is a honeypot designed to be a one click installable,            #
#   open source honey-pot that any developer or administrator would be able    #
#   to write custom plugins for based on specific needs.                       #
#   Copyright (C) 2016 RECCE7                                                  #
#                                                                              #
#   This program is free software: you can redistribute it and/or modify       #
#   it under the terms of the GNU General Public License as published by       #
#   the Free Software Foundation, either version 3 of the License, or          #
#   (at your option) any later version.                                        #
#                                                                              #
#   This program is distributed in the hope that it will be useful,            #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See their            #
#   GNU General Public License for more details.                               #
#                                                                              #
#   You should have received a copy of the GNU General Public licenses         #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
################################################################################

import platform
import socket

from common.logger import Logger
from recon.ipinfoagent import IPInfoAgent
from threading import Thread, Lock

__author__ = 'Jesse Nelson <jnels1242012@gmail.com>, ' \
             'Randy Sorensen <sorensra@msudenver.edu>'


class NetworkListener(Thread):
    def __init__(self, listening_address, config, framework):
        super().__init__()
        self._config = config
        self._listening_address = listening_address
        self._port = config['port']
        self._framework = framework
        self._session_socket = None
        self._lock = Lock()
        self._running = False
        self.__connection_count = 0
        self._logger = Logger().get('framework.networklistener.NetworkListener')

    @property
    def connection_count(self):
        with self._lock:
            return self.__connection_count

    @connection_count.setter
    def connection_count(self, val):
        with self._lock:
            self.__connection_count = val

    # Override
    def run(self):
        self._running = True
        self._logger.info('%s plugin listener started on port %d'
                          % (self._config['moduleClass'], self._port))
        while self._running:
            try:
                self._session_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                self._session_socket.setsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self._session_socket.bind((self._listening_address, self._port))
                self._session_socket.listen(1)
                self.start_listening(self._session_socket)
                self._session_socket.close()
                self.connection_count += 1
            except OSError as e:
                if e.errno == 24:
                    self._logger(self._config['instanceName'] + ': Too many open files.')
                    self._running = False
            except Exception as e:
                self._logger.warn(str(e))
        self._logger.info('%s plugin listener on port %d shutting down'
                          % (self._config['moduleClass'], self._port))
        self._session_socket = None

    def start_listening(self, local_socket):
        try:
            (new_socket, addr) = local_socket.accept()
            if self._running:
                self._logger.info('New connection from %s on port %d'
                                  % (addr, self._port))
                self._framework.spawn(new_socket, self._config)

                ipinfo_agent = IPInfoAgent(addr[0], self._framework,
                                           self._config['instanceName'])
                ipinfo_agent.start()
        except ConnectionAbortedError as e:
            if not self._running:
                return
            raise e
        except OSError as e:
            if e.errno == 22 and not self._running:
                return
            if e.errno == 24:
                self._logger(self._config['instanceName'] + ': Too many open files.')
                self._running = False
                return
            raise e
        except Exception as e:
            self._logger.error('Error on connection: %s' % e)
            raise e

    def shutdown(self):
        self._running = False
        try:
            if self._session_socket:
                if platform.system() == 'Linux':
                    self._session_socket.shutdown(socket.SHUT_RDWR)
                else:
                    self._session_socket.close()
        except Exception as e:
            self._logger.warn('while closing socket: ' + str(e))
        self.join()

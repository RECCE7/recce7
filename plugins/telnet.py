################################################################################
#                                                                              #
#                           GNU Public License v3.0                            #
#                                                                              #
################################################################################
#   HunnyPotRx is a honeypot designed to be a one click installable,           #
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

"""
"""

from math import ceil
from plugins.base import BasePlugin
from socket import SocketIO


def set_command(help_description):
    def func_decorator(function):
        function.get_command = True
        function.get_description = help_description
        return function

    return func_decorator


class TelnetPlugin(BasePlugin):
    def __init__(self, socket, config, framework):
        BasePlugin.__init__(self, socket, config, framework)
        self.input_type = ''
        self.user_input = ''
        self.io = SocketIO(self._skt, "rw")
        self._session = None

    def do_track(self):
        self.get_session()

        self.username()
        self.password()
        self.options()
        while self._skt and not self.kill_plugin:
            self.command()

    def get_session(self):
        self._session = str(self.get_uuid4())

    def close_descriptors(self):
        self.io.close()

    def get_input(self):
        try:
            data = self.io.readline(1024).decode()
        except OSError:
            self.kill_plugin = True
            return

        data = data.strip('\r\n')
        data = data.strip('\n')
        return data

    def username(self):
        self.io.write(b'Username: ')

        self.input_type = 'username'
        self.user_input = self.get_input()
        self.do_save()

    def password(self):
        self.io.write(b'Password: ')

        self.input_type = 'password'
        self.user_input = self.get_input()
        self.do_save()

    def command(self):
        self.input_type = 'command'
        self.io.write(b'. ')

        line = self.get_input()
        commands = line.split(';')

        for i in commands:
            if self.kill_plugin:
                break
            self.handle(i)

    def handle(self, command):
        if len(command) == 0:
            return

        self.input_type = 'command'
        self.user_input = command
        self.do_save()

        arguments = command.split(' ', 1)
        command = arguments.pop(0)

        if self.is_command(command):
            if len(arguments) == 0:
                getattr(self, command)()
            else:
                getattr(self, command)(arguments.pop(0))
        else:
            self.io.write(b'%unrecognized command - type options for a list\r\n')

    def is_command(self, command):
        if hasattr(self, command):
            if hasattr(getattr(self, command), 'get_command'):
                return True
            else:
                return False
        else:
            return False

    @set_command('basic list of options available to user')
    def options(self, arguments=None):
        self.io.write(b'\r\nWelcome, Please choose from the following options\r\n')
        line_count = 0
        for option in dir(self):
            if self.is_command(option):
                if line_count == 5:
                    self.io.write(b'\r\n')
                    line_count = 0

                tabs = b''
                i = 0
                try:
                    for i in range(0, ceil((16 - len(option)) / 8)):
                        tabs += b'\t'
                except ZeroDivisionError:
                    tabs = ':'
                self.io.write(option.encode() + tabs)
                line_count += 1
        self.io.write(b'\r\n')

    @set_command('detailed description of options')
    def help(self, arguments=None):
        for help in dir(self):
            if self.is_command(help):
                tabs = b':'
                i = 0
                try:
                    for i in range(0, ceil((16 - len(help) - 1) / 8)):
                        tabs += b'\t'
                except ZeroDivisionError:
                    tabs = ':'
                self.io.write(help.encode() + tabs + getattr(getattr(self, help), 'get_description').encode() + b'\r\n')

    @set_command('prompt to echo back typing')
    def echo(self, arguments=None):
        self.input_type = 'echo'
        if arguments:
            self.user_input = arguments
        else:
            self.io.write(b'Text? ')
            self.user_input = self.get_input()
            self.do_save()
        self.io.write(self.user_input.encode() + b'\r\n')

    @set_command('close telnet connection to server')
    def quit(self, arguments=None):
        self.io.write(b'\nGoodbye\n')
        self.io.close()
        self.kill_plugin = True

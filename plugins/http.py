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


from plugins.base import BasePlugin
from socket import SocketIO
from socket import timeout
from http.server import BaseHTTPRequestHandler
from http.server import _quote_html

PAGE_LOGIN = b"""<html>
    <head>
        <style>
            form {
                text-align: center;
            }
        </style>
        <section class="loginform cf">
        <form action="login" method="post">
            Username<br>
            <input type="text" name="username" required><br>
            Password<br>
            <input type="password" name="password" required><br>
            <input type="submit" value="Login">
        </form>
        </section>
    </head>
</html>"""

GOOD_PATHS = [
    '/',
    '/index.html',
]

MAX_MESSAGE_LENGTH = 65536


class HTTPPlugin(BasePlugin, BaseHTTPRequestHandler):
    def __init__(self, socket, config, framework):
        BasePlugin.__init__(self, socket, config, framework)

        self.rfile = SocketIO(socket, "r")
        self.wfile = SocketIO(socket, "w")

        socket.settimeout(60)

    def do_track(self):
        self.handle_one_request()
        self.format_data()
        self.do_save()
        self.kill_plugin = True

    def close_descriptors(self):
        self.rfile.close()
        self.wfile.close()

    def get_body(self):
        too_long = False

        if not hasattr(self, 'headers'):
            return

        else:

            try:
                body_length = int(self.headers.get('content-length', 0))
                if body_length > 65536:
                    body_length = 65536
                    too_long = True
            except TypeError:
                self.body = ''
                return

            try:
                self.body = self.rfile.read(body_length)
                self.body = str(self.body, 'utf-8')
                if too_long:
                    self.body += '*'
            except timeout:
                self.body = ''

    def get_session(self):
        if not hasattr(self, 'headers'):
            return

        try:
            cookie = self.headers.get('cookie', None)
        except AttributeError:
            cookie = self.get_uuid4()
            self.send_header('Set-Cookie', 'SESSION=' + cookie)
            return

        if cookie is None:
            cookie = self.get_uuid4()
        else:
            cookie = cookie.split("SESSION=")
            if len(cookie) > 1:
                cookie = cookie[1].split()[0]

        self.send_header('Set-Cookie', 'SESSION=' + cookie)
        self._session = cookie

    def format_data(self):
        if not hasattr(self, 'command'):
            self.command = ''
        if not hasattr(self, 'path'):
            self.path = ''
        if not hasattr(self, 'headers'):
            self.headers = ''
        else:
            self.headers = self.headers.as_string()
        if not hasattr(self, 'body'):
            self.body = ''

    def address_string(self):
        return self._skt.getsockname()[0]

    def end_headers(self):
        self.get_session()
        if self.request_version != 'HTTP/0.9':
            self._headers_buffer.append(b"\r\n")
            self.flush_headers()

    def do_GET(self):
        if self.path in GOOD_PATHS:
            self.do_HEAD()
            self.wfile.write(PAGE_LOGIN)
        else:
            self.send_error(404)

    def do_HEAD(self):
        if self.path in GOOD_PATHS:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Connection', 'close')
            self.send_header('Content-Length', str(len(PAGE_LOGIN)))
            self.end_headers()
        else:
            content = (self.error_message_format %
                   {'code': 404, 'message': _quote_html('File not found'),
                    'explain': _quote_html('Nothing matches the given URI')})
            body = content.encode('UTF-8', 'replace')
            self.send_response(404, "File not found")
            self.send_header("Content-Type", self.error_content_type)
            self.send_header('Connection', 'close')
            self.send_header('Content-Length', int(len(body)))
            self.end_headers()

    def do_POST(self):
        self.get_body()
        if self.path in GOOD_PATHS:
            self.do_GET()
        elif self.path == '/login':
            self.send_error(403)
        else:
            self.send_error(404)

    def do_PUT(self):
        self.send_error(501)

    def do_OPTIONS(self):
        self.send_error(501)

    def do_DELETE(self):
        self.send_error(501)

    def do_TRACE(self):
        self.send_error(501)

    def do_CONNECT(self):
        self.send_error(501)
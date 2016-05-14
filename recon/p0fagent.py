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

from common.globalconfig import GlobalConfig
from common.logger import Logger
from datetime import datetime
from datetime import timedelta
from p0f import P0f, P0fException
from threading import Thread


class P0fAgent(Thread):
    def __init__(self, peer_address, framework, session):
        super().__init__()
        self.config = GlobalConfig()
        self.framework = framework
        self.fs_sock = self.config['Framework']['p0f.fs_sock']
        self.log = Logger().get('recon.p0fagent.P0fAgent')
        self.peer_address = peer_address
        self.session = session

    def run(self):
        p0f = P0f(self.fs_sock)
        peer_info = None
        try:
            peer_info = p0f.get_info(self.peer_address)
        except P0fException as e:
            self.log.warn('p0f request failed for ' +
                          self.peer_address +
                          ': ' + str(e))
            return
        except KeyError as e:
            self.log.warn('p0f couldn\'t find any info for ' +
                          self.peer_address)
            return
        except ValueError as e:
            self.log.warn('p0f returned bad data for ' +
                          self.peer_address)
            return
        except FileNotFoundError as e:
            self.log.error('p0f filesystem socket not found')
            return
        except Exception as e:
            self.log.error('unknown p0f error occurred on address ' +
                           self.peer_address + ': ' + str(e))
            return

        # prettify C/null-terminated byte arrays in p0f info dict
        for key in peer_info.keys():
            if type(peer_info[key]) == bytes:
                decoded = peer_info[key].decode('utf-8')
                peer_info[key] = decoded.partition('\x00')[0]
            elif type(peer_info[key]) == datetime:
                peer_info[key] = peer_info[key].isoformat()
            elif type(peer_info[key]) == timedelta:
                peer_info[key] = str(int(peer_info[key].total_seconds()))
            elif type(peer_info[key]) == int:
                peer_info[key] = str(peer_info[key])

        data = { 'p0f': {
                 'session': self.session,
                 'first_seen': peer_info['first_seen'],
                 'last_seen': peer_info['last_seen'],
                 'uptime': peer_info['uptime'],
                 'last_nat': peer_info['last_nat'],
                 'last_chg': peer_info['last_chg'],
                 'distance': peer_info['distance'],
                 'bad_sw': peer_info['bad_sw'],
                 'os_name': peer_info['os_name'],
                 'os_flavor': peer_info['os_flavor'],
                 'os_match_q': peer_info['os_match_q'],
                 'http_name': peer_info['http_name'],
                 'http_flavor': peer_info['http_flavor'],
                 'total_conn': peer_info['total_conn'],
                 'link_type': peer_info['link_type'],
                 'language': peer_info['language']
             }
        }
        self.framework.insert_data(data)

        self.log.debug('p0f info for ' +
                       self.peer_address +
                       ': ' +
                       str(peer_info))

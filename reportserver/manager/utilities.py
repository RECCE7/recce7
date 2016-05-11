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

from common.logger import Logger
from reportserver.manager.UnitOfMeasure import UnitOfMeasure
import dateutil.parser
import socket



#Given a string, try to convert it to an int.
def validate_port_number(givenStr):
    log = Logger().get('reportserver.manager.utilities')
    log.debug("given str is: " + givenStr)

    try:
        return int(givenStr)
    except Exception as e:
        log.error("Error:  Received invalid string to convert to int: " + givenStr)
        log.error (str(e))
        return None


#Given a token
def validate_time_period(query_tokens):
    log = Logger().get('reportserver.manager.utilities')
    log.debug("given query_tokens:" + str(query_tokens))

    uom = None
    units = None

    for token in query_tokens:
        if '=' in token:
            uom,units = token.split('=')
            if uom in UnitOfMeasure.get_values(UnitOfMeasure):
                units = int(units)
                break
            else:
                uom  = None
                units = None

    # default if we aren't given valid uom and units
    #TODO:  get this from a config file.
    if uom is None or units is None:
        uom = "days"
        units = 1

    log.debug("validate_time_period: " + str(uom) + ": " + str(units))
    return (uom, units)

def get_path_query_tokens(path):
    path_query_tokens = path.split('?')
    query_tokens = []

    path_tokens = path_query_tokens[0].split('/')
    #print('#debug path tokens: ', path_tokens)

    if len(path_query_tokens) > 1:
        query_tokens = path_query_tokens[1].split('&')
        #print('#debug query tokens: ', query_tokens)


    return path_tokens, query_tokens


#Given a string, check that it is a format of an ipaddress
def validate_ipaddress(givenStr):
    try:
        socket.inet_aton(givenStr)  #works only on IPv4
    except socket.error:
        raise ValueError("ipAddress given is invalid, please recheck")

    return givenStr


#Process data from the list of results from the database.
#Results is a list of dictionaries
def process_data(results):
    if (results == None or len(results) == 0):
        return results

    # we know we have more than one row
    first_row = results[0]
    current_session = first_row['session']
    port_data_json = []  # object to return at end of day.

    session_json = setup_session_json(first_row)  # port_data_json is a list of these
    session_rows = []  # session_json has a list of these

    for row in results:
        # handle session changes
        if (row['session'] != current_session):
            session_json['session_items'] = session_rows.copy()
            session_json['duration'] = get_date_delta(session_json['begin_time'], session_json['end_time'])
            port_data_json.append(session_json)
            session_rows.clear()
            current_session = row['session']
            session_json = setup_session_json(row)
        # append each row
        session_rows.append(row)
        session_json['end_time'] = row['eventDateTime']

    # handle the end of rows here
    session_json['session_items'] = session_rows.copy()
    session_json['duration'] = get_date_delta(session_json['begin_time'], session_json['end_time'])
    port_data_json.append(session_json)

    return port_data_json

#Defining the json output for a session header
def setup_session_json(row):
    session_json = {
        'session': row['session'],
        'begin_time': row['eventDateTime'],
        'end_time': row['eventDateTime'],
        'local_address': row['localAddress'],
        'peer_address': row['peerAddress']
    }
    return session_json


#determining the duration of a session using from and to iso dates.
def get_date_delta(iso_date_from, iso_date_to):
    try:
        date_from = dateutil.parser.parse(iso_date_from)
        date_to = dateutil.parser.parse(iso_date_to)
        delta = date_to - date_from
    except Exception as e:
        log = Logger().get('reportserver.manager.utilities')
        log.error("Error: " + str(e))
        delta = 0

    return str(delta)
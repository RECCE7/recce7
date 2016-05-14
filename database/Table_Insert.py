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
__author__ = 'Ben Phillips'


import sqlite3

from common.globalconfig import GlobalConfig
from common.logger import Logger
from database.util import *

def insert_data(name, data_list, session_value, has_id=False):
    config = GlobalConfig()
    connection = sqlite3.connect(config['Database']['path'])
    cursor = connection.cursor()
    Logger().get('database.Table_Insert').debug(data_list)

    delimiter = ','
    param_placeholder = delimiter.join('?' * len(data_list))
    has_id_str = ('' if not has_id else 'null,')
    insert_string = 'insert into ' + name + ' values(' + has_id_str + param_placeholder + ')'
    cursor.execute(insert_string, data_list)

    if session_value is not None:
        session_recorded_sessions = cursor.execute('select count(session) from sessions where session = "' + session_value + '" and table_name = "' + name + '"').fetchall()
        if session_recorded_sessions[0][0] > 0 or name == 'p0f':
            pass
        else:
            cursor.execute('insert into sessions values("' + session_value + '","' + name + '")')

    connection.commit()
    connection.close()


def update_data(name, data_list, table_schema, where_string):
    config = GlobalConfig()
    connection = sqlite3.connect(config['Database']['path'])
    cursor = connection.cursor()
    Logger().get('database.Table_Insert').debug(data_list)

    update_list = []
    for i in range(len(table_schema)):
        quote = ''
        if type(data_list[i]) == str:
            quote = '\''
        elif type(data_list[i]) == type(None):
            data_list[i] = 'NULL'
        update_list.append(table_schema[i][1] +
                           ' = ' +
                           quote + str(data_list[i]) + quote
        )

    delimiter = ','
    update_string = delimiter.join(['%s'] * len(update_list))
    update_sql_string = 'update ' + name + ' set ' + update_string + ' ' + where_string
    update_str = update_sql_string % tuple(update_list)
    cursor.execute(update_str)
    connection.commit()
    connection.close()


# we should already know the data is good but now we should break the
# dictionary into a table name and a list of data to insert into the
# table. We must also sort the list according to the table structure
# then call the insert_data method

def prepare_data_for_insertion(schema, data):
    # Look for "special" tables
    # if 'p0f' in data:
    #     insert_p0f_data(data)
    #     return
    config = GlobalConfig()
    connection = sqlite3.connect(config['Database']['path'])
    cursor = connection.cursor()
    #get the correct table schema we want to sort to
    table_schema = schema[get_first_key_value_of_dictionary(data)]
    #print(table_schema)
    #break the table/data dictionary into a table name and a dictionary of data
    table_name = get_first_key_value_of_dictionary(data)
    #print(table_name)
    data_dict = data[table_name]

    #session extraction
    session_value = None
    if 'session' in data_dict:
        session_value = data_dict.get('session')

    #build a list of data in the correct order
    Logger().get('database.Table_Insert').debug('Inserting Data: ' + str(data_dict))
    insert_list = []
    has_id = False
    for col in table_schema:
        if col[1] == 'ID':
            has_id = True
            pass
        elif col[1] not in data_dict:
            insert_list.append(None)
        else:
            insert_list.append(data_dict[col[1]])

    plugin_tables = []
    for port in GlobalConfig().get_plugin_dictionary():
        config_dict = GlobalConfig().get_plugin_config(port)
        plugin_tables.append(config_dict['table'])

    if table_name in plugin_tables:
        insert_data(table_name,insert_list,session_value, has_id)

    elif table_name == 'p0f':
        if session_value:
            session_recorded_p0f = cursor.execute(
                'select count(session) '
                'from p0f '
                'where session = "' + session_value + '"').fetchall()
            if session_recorded_p0f[0][0] > 0:
                where_string = 'where session = ' + '"' + session_value + '"'
                update_data(table_name, insert_list, table_schema, where_string)
            else:
                insert_data(table_name, insert_list, session_value, has_id)

    elif table_name == 'ipInfo':
        count_query = ('select count(*) ' +
                       'from ipInfo ' +
                       'where ip = \'' + data_dict['ip'] + '\' ' +
                       'and plugin_instance = \'' + data_dict['plugin_instance'] + '\'')
        ip_recorded = cursor.execute(count_query).fetchall()
        if ip_recorded[0][0] > 0:
            pass
        else:
            insert_data(table_name, insert_list, None , has_id)

    connection.commit()
    connection.close()
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

import os
import sqlite3

from copy import deepcopy


# Column format: [Name, Type, Constraint List ...]
default_columns = [
    ['ID', 'INTEGER', 'NOT NULL', 'PRIMARY KEY'],
    ['session', 'TEXT', 'NULL'],
    ['eventDateTime', 'TEXT', 'NULL'],
    ['peerAddress', 'TEXT', 'NULL'],
    ['localAddress', 'TEXT', 'NULL']
]


def remove_default_columns_from_list(collection):
    collection_copy = deepcopy(collection)
    if isinstance(collection_copy,list):
        for col in default_columns:
            if col[0] in collection_copy:
                collection_copy.remove(col[0])
        return collection_copy

    if isinstance(collection_copy,dict):
        for col in default_columns:
            if col[0] in collection_copy:
                del collection_copy[col[0]]
        return collection_copy


def get_first_key_value_of_dictionary(value):
    """
    Gets the only key in a dictionary.

    :param value: a single-item dictionary
    :return: a string
    """
    return next(iter(value.keys()))


def run_db_scripts(global_config):
    """
    this method will run all db scripts in the scripts directory to create
    non-user defined sqlite objects
    """
    connection = sqlite3.connect(global_config['Database']['path'])
    cursor = connection.cursor()
    script_path = '/database/sql_scripts'
    file_list = os.listdir(os.getcwd() + script_path)
    for file_name in file_list:
        with open(os.getcwd() + script_path + '/' + file_name,'r') as file:
            cursor.execute(file.read())
    connection.close()


def get_config_table_list(port_list, schema_dict):
    """
    Given a list of ports and a corresponding config dict,
    return a list of tables that correspond to those ports.

    :param port_list: a list of ports
    :param schema_dict: the config dict defining each port

    :return: a list of table names
    """
    config_table_list = []
    for port in port_list:
        config = schema_dict[port]
        config_table_list.append(config['table'])
    return config_table_list

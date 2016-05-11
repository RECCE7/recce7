import sqlite3
import os

from database.util import *
from operator import itemgetter

__author__ = 'Ben Phillips'

# create a table in the sqlite database with the name of the table passed in

# this list contains the default columns that the base plugin will control

# this is useful because when we are verifying that all of the columns provided
# by the custom plugin are indeed in the database we can ignore these programatically
# as they are not controlled by the author


def create_table(name, global_config):
    connection = sqlite3.connect(global_config['Database']['path'])
    cursor = connection.cursor()

    default_column_list = []
    for col in default_columns:
        default_column_list.append(' '.join(col))
    default_column_def = ','.join(default_column_list)

    cursor.execute('CREATE TABLE ' + name + '(' + default_column_def + ')')
    connection.close()

def create_index(cfg_tables, global_config):
    connection = sqlite3.connect(global_config['Database']['path'])
    cursor = connection.cursor()
    for name in cfg_tables:
        cursor.execute('CREATE INDEX IF NOT EXISTS DT_IDX_' + name + ' ON ' + name + ' (eventDateTime)')
    connection.close()

def add_columns(name, column_list, global_config):
    """
    add columns to the table, requires the name of the table and the column list
    this column list currently contains [column order],[column name],[column type]
    """
    verify_data_types(column_list)
    connection = sqlite3.connect(global_config['Database']['path'])
    cursor = connection.cursor()
    column_list_sorted = sorted(column_list, key=itemgetter(0))
    for x in column_list_sorted:
        cursor.execute('ALTER TABLE ' + name + ' ADD COLUMN ' + x[1] + ' ' + x[2])
    connection.close()


def verify_data_types(column_list):
    """
    check that the data types passed in are valid sqlite data types
    """
    valid_data_types = ('NULL', 'INTEGER', 'REAL', 'TEXT', 'BLOB')
    for row in column_list:
        if row[2] in valid_data_types:
            pass
        else:
            raise ValueError('Verifying ' + str(row) + ' : ' + row[2] +
                             ' is not a valid SQLITE3 data type')


def check_table_exists(name, global_config):
    """
    check if table name exists, is case sensitive
    """
    connection = sqlite3.connect(global_config['Database']['path'])
    cursor = connection.cursor()
    table_count = cursor.execute(
        "SELECT count(*) " +
        "FROM sqlite_master " +
        "WHERE type='table' " +
        "AND name='" + name + "';").fetchall()
    connection.close()
    if table_count[0][0] > 0:
        return True
    else:
        return False


def change_table_structure(name, config_column_list, db_column_list, global_config):
    # rename old table
    connection = sqlite3.connect(global_config['Database']['path'])
    cursor = connection.cursor()
    cursor.execute("ALTER TABLE " + name + " RENAME TO " + name + "_delme")

    # create new table
    create_table(name, global_config)

    add_columns(name, config_column_list, global_config)

    #
    # TODO: Copy old data to new table.
    #
    #   WARNING: you'll lose data if the columns aren't there in the new
    #            table!
    #
    # To do this, we need to find columns in common between database and
    # config.
    #

    # remove old table
    delete_table(name, global_config)


def delete_table(name, global_config):
    connection = sqlite3.connect(global_config['Database']['path'])
    cursor = connection.cursor()

    # if you are deleting a table due to changing the configuration of the
    # columns, let's remove any sessions from the sessions table referencing
    # the old table

    if cursor.execute(
            "SELECT count(*) " +
            "FROM sqlite_master " +
            "WHERE type='table' " +
            "AND name='" + name + "_delme';").fetchall()[0][0] > 0:
        cursor.execute(
            "DELETE FROM sessions " +
            "WHERE table_name = '" + name + "';")
    # drop index first
    cursor.execute("DROP INDEX IF EXISTS DT_IDX_" + name)
    # drop table
    cursor.execute("DROP TABLE IF EXISTS " + name + "_delme;")

    cursor.close()

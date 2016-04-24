import sqlite3

from common.logger import Logger
from copy import deepcopy
from database import Table_Init

__author__ = 'Ben Phillips'

#
# this file will validate data and provide functionality to sort
# data by the columns defined in the database
#


class DataValidation:
    def __init__(self,global_config_instance):
        self.table_schema = {}
        self.tables = []
        self.log = Logger().get('database.DataValidation.DataValidation')
        connection = sqlite3.connect(global_config_instance['Database']['path'])
        cursor = connection.cursor()
        #will want to loop here through all tables found and store each schema
        #as an element in a list, this will require code changes throughout this file
        rows = cursor.execute("select name from sqlite_master where type = 'table';").fetchall()
        #transform list of tuples to a list of strings
        for row in rows:
            self.tables.append(row[0])
        for table in self.tables:
            table_def = cursor.execute('PRAGMA table_info(' + table + ');').fetchall()
            self.table_schema[table] = table_def
        cursor.close()

    # for updating tables and table schema class variables
    def update_tables_and_schema(self,global_config_instance):
        self.table_schema.clear()
        del self.tables[:]
        connection = sqlite3.connect(global_config_instance['Database']['path'])
        cursor = connection.cursor()
        #will want to loop here through all tables found and store each schema
        #as an element in a list, this will require code changes throughout this file
        rows = cursor.execute("select name from sqlite_master where type = 'table';").fetchall()
        #transform list of tuples to a list of strings
        for row in rows:
            self.tables.append(row[0])
        for table in self.tables:
            table_def = cursor.execute('PRAGMA table_info(' + table + ');').fetchall()
            self.table_schema[table] = table_def
        cursor.close()

    # return the class level variable tables
    def get_tables(self):
        return self.tables

    # return the class level variable table_schema
    def get_schema(self):
        return self.table_schema

    # Ensure exactly one table is written to at a time
    def check_value_len(self, value):
        if len(value) != 1:
            self.log.error('Plugin tried to save ' +
                           str(len(value)) +
                           'table(s) in one save')
            return False
        return True

    # Checks that the value is actually a dictionary
    def check_value_is_dict(self, value):
        if not isinstance(value, dict):
            self.log.error('Plugin attempted to save non-dictionary type: ' +
                           type(value))
            return False
        return True

    # Checks that the key in the dictionary is a string
    def check_key_in_dict_string(self, value):
        key = DataValidation.get_first_key_value_of_dictionary(value)
        if not isinstance(key, str):
            self.log.error('Table name must be a string: got ' +
                           type(key) +
                           ' instead')
            return False
        return True

    # Checks that the key in the dictionary is
    # a real table name in the database
    def check_key_is_valid_table_name(self,value):
        table_name = DataValidation.get_first_key_value_of_dictionary(value)
        if table_name not in self.tables:
            self.log.error('No such table: ' + table_name)
            return False
        return True

    # Checks that the row data is actually a dictionary
    def check_row_value_is_dict(self,value):
        key = self.get_first_key_value_of_dictionary(value)
        if not isinstance(value.get(key), dict):
            self.log.error('Row data must be a dictionary: got ' +
                           type(value.get(key)) +
                           ' instead')
            return False
        return True

    #gets the first key value in a dictionary
    @staticmethod
    def get_first_key_value_of_dictionary(value):
        return next(iter(value.keys()))

    #checks that all of the keys in the row data are strings
    def check_all_col_names_strings(self,value):
        key = self.get_first_key_value_of_dictionary(value)
        dict = value.get(key)
        count = len(dict.keys())
        compare = 0
        for key in dict.keys():
            if isinstance(key,str):
                compare += 1
        return count == compare

    # Verifies that no additional columns were provided by a
    # plugin that aren't referred to in the database schema.
    def check_all_col_exist(self,value):
        key = self.get_first_key_value_of_dictionary(value)
        schema = self.table_schema[key]

        # remove default columns because we do not require the plugin author
        # to provide these
        schema_col_list = DataValidation.remove_default_columns_from_list([row[1] for row in schema])

        # get a list of column names from the table referenced in value
        prep_list = DataValidation.remove_default_columns_from_list(value[key])
        col_list = list(prep_list.keys())

        extra_cols = set(col_list) - set(schema_col_list)
        if len(extra_cols) > 0:
            self.log.error('Unknown column(s) in table \'' + key + '\': ' + str(extra_cols))
            return False
        return True

    @staticmethod
    def remove_default_columns_from_list(collection):
        collection_copy = deepcopy(collection)
        if isinstance(collection_copy,list):
            for col in Table_Init.default_columns:
                if col[0] in collection_copy:
                    collection_copy.remove(col[0])
            return collection_copy

        if isinstance(collection_copy,dict):
            for col in Table_Init.default_columns:
                if col[0] in collection_copy:
                    del collection_copy[col[0]]
            return collection_copy

    # TODO determine how to do this with regex
    def check_data_types(self, value):
        return True

    def run_all_checks(self, value):
        return (self.check_value_len(value) and
                self.check_value_is_dict(value) and
                self.check_key_in_dict_string(value) and
                self.check_key_is_valid_table_name(value) and
                self.check_row_value_is_dict(value) and
                self.check_all_col_names_strings(value) and
                self.check_all_col_exist(value) and
                self.check_data_types(value))

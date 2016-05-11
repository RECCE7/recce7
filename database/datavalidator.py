from common.globalconfig import GlobalConfig
from common.logger import Logger
from database.util import *

__author__ = 'Ben Phillips'

#
# this file will validate data and provide functionality to sort
# data by the columns defined in the database
#


class DataValidator:
    def __init__(self):
        self.config = GlobalConfig()
        self.table_schema = {}
        self.tables = []
        self.log = Logger().get('database.datavalidator.DataValidator')
        self.get_schema_from_database()

    # for updating tables and table schema class variables
    def update_tables_and_schema(self):
        self.table_schema.clear()
        self.tables.clear()
        self.get_schema_from_database()

    def get_schema_from_database(self):
        connection = sqlite3.connect(self.config['Database']['path'])
        cursor = connection.cursor()
        #will want to loop here through all tables found and store each schema
        #as an element in a list, this will require code changes throughout this file
        db_rows = cursor.execute(
            "SELECT name "
            "FROM sqlite_master "
            "WHERE type = 'table';").fetchall()
        #transform list of tuples to a list of strings
        for row in db_rows:
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
                           str(type(value)))
            return False
        return True

    # Checks that the key in the dictionary is a string
    def check_key_in_dict_string(self, value):
        key = get_first_key_value_of_dictionary(value)
        if not isinstance(key, str):
            self.log.error('Table name must be a string: got ' +
                           str(type(key)) +
                           ' instead')
            return False
        return True

    # Checks that the key in the dictionary is
    # a real table name in the database
    def check_key_is_valid_table_name(self,value):
        table_name = get_first_key_value_of_dictionary(value)
        if table_name not in self.tables:
            self.log.error('No such table: ' + table_name)
            return False
        return True

    # Checks that the row data is actually a dictionary
    def check_row_value_is_dict(self,value):
        key = get_first_key_value_of_dictionary(value)
        if not isinstance(value.get(key), dict):
            self.log.error('Row data must be a dictionary: got ' +
                           str(type(value.get(key))) +
                           ' instead')
            return False
        return True

    #checks that all of the keys in the row data are strings
    def check_all_col_names_strings(self,value):
        key = get_first_key_value_of_dictionary(value)
        dict = value.get(key)
        count = len(dict.keys())
        compare = 0
        for key in dict.keys():
            if isinstance(key,str):
                compare += 1
        return count == compare

    # Verifies that no additional columns were provided by a
    # plugin that aren't referred to in the database schema.
    def check_all_col_exist(self, value):
        key = get_first_key_value_of_dictionary(value)
        schema = self.table_schema[key]

        # remove default columns because we do not require the plugin author
        # to provide these
        schema_col_list = remove_default_columns_from_list([row[1] for row in schema])

        # get a list of column names from the table referenced in value
        prep_list = remove_default_columns_from_list(value[key])
        col_list = list(prep_list.keys())

        extra_cols = set(col_list) - set(schema_col_list)
        if len(extra_cols) > 0:
            self.log.error('Unknown column(s) in table \'' + key + '\': ' + str(extra_cols))
            return False
        return True

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

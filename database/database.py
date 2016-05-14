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
import ntpath

from common.globalconfig import GlobalConfig
from common.logger import Logger
from database import Table_Init
from database.util import *
from database.datavalidator import DataValidator

__author__ = 'Ben Phillips'


class Database:
    def __init__(self):
        self.global_config = GlobalConfig()
        self.log = Logger().get('database.database.Database')

    def create_default_database(self):
        """
        Calls methods needed to create the database.
        """
        self.create_db_dir()
        self.create_db()

        # Execute scripts BEFORE updating schema
        run_db_scripts(self.global_config)

        self.update_schema()


    def create_db_dir(self):
        """
        Creates the database directory if it doesn't already exist.
        """

        # if database directory does not exist create it
        db_path = self.global_config['Database']['path']
        (db_dir, db_name) = ntpath.split(db_path)
        if not os.path.isdir(db_dir):
            self.log.info("Database directory not found, "
                          "creating database directory...")
            os.mkdir(db_dir)
    
    def create_db(self):
        """
        Creates the database if it doesn't already exist.
        """

        # if database file does not exist in the directory, create it
        (db_dir, db_name) = ntpath.split(self.global_config['Database']['path'])
        if not os.path.exists(self.global_config['Database']['path']):
            self.log.info("Database file not found, creating database file...")

            # this actually creates the database file
            connection = sqlite3.connect(self.global_config['Database']['path'])
            connection.close()
    
    def update_schema(self):
        """
        Updates the database when columns have been added to, or
        removed from, the schema.
        """

        # Create any new tables that have been added to the plugin
        # config schema.
        db_tables = DataValidator().get_tables()
        cfg_tables = get_config_table_list(
            self.global_config.get_ports(),
            self.global_config.get_plugin_dictionary())
        table_diff = list(set(cfg_tables) - set(db_tables))
        self.create_non_exist_tables(table_diff)

        # Populate the newly created tables with their column
        # definitions.
        DataValidator().update_tables_and_schema()
        self.update_table_structure()
        #create indexes on plugin tables if they do not exist
        Table_Init.create_index(cfg_tables,self.global_config)


    def create_non_exist_tables(self, table_diff):
        """
        create tables that do not exist from the table difference between the current database and the configuration
        """
        if len(table_diff) > 0:
            for table in table_diff:
                Table_Init.create_table(table, self.global_config)
            self.log.info('Updated database schema, table names now match configuration.')
        else:
            self.log.info('Database Schema and Configuration table names already match.')
    
    def create_dict_config_column_list(self):
        """
        get a dictionary of tables and corresponding columns from the config
        """
        config_column_lists = {}
        for port in self.global_config.get_ports():
            value = self.global_config.get_plugin_dictionary().get(port)
            config_column_lists[value.get('table')] = value.get('tableColumns')
        return config_column_lists

    def create_dict_transformed_column_list(self, database_column_lists):
        """
        returns only custom plugin defined columns from database schema i.e.
        ignores default columns
        """
        transformed_db_column_list = {}
        for table in database_column_lists:
            col_list = database_column_lists[table]
            transformed_db_column_list[table] = []
            # default column ids to ignore
            default_list = []
            for default in default_columns:
                default_list.append(default[0])
            for column in col_list:
                # ignores the default columns
                if column[1] in default_list:
                    continue
                transformed_db_column_list[table].append([column[0],column[1],column[2]])
        return transformed_db_column_list
    
    def update_table_structure(self):
        cfg_schema = self.create_dict_config_column_list()
        db_schema = DataValidator().get_schema()
        db_schema_sans_defaults = self.create_dict_transformed_column_list(db_schema)

        for table in cfg_schema:
            if not [(x[1], x[2]) for x in cfg_schema[table]] == \
                   [(x[1], x[2]) for x in db_schema_sans_defaults[table]]:
                Table_Init.change_table_structure(
                    table, cfg_schema[table], db_schema[table],
                    self.global_config)

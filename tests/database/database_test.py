import unittest
from database import database
from database import datavalidator
from common.globalconfig import GlobalConfig
from unittest.mock import patch
from common.logger import Logger
import os
import shutil
from database import util






class database_test(unittest.TestCase):

    def setUp(self):
        self.test_db_dir = '/tests/database/test_database'
        self.test_db_file = '/tests/database/test_database/honeyDB.sqlite'
        # test configuration files
        self.plugins_config_file = 'tests/database/test_config/plugins.cfg'
        self.plugins_config_diff_file = 'tests/database/test_config/plugins_diff.cfg'
        self.plugins_config_diff_table_file = 'tests/database/test_config/plugins_diff_table.cfg'
        self.global_config_file = 'tests/database/test_config/global.cfg'
        # create global config instance
        self.gci = GlobalConfig(self.plugins_config_file,self.global_config_file)
        self.gci.read_global_config()
        self.gci.read_plugin_config()

    # patch the Logger new method so that it doesn't create the log file, we do not need to test that the logging
    # works just that the log statements are called.
    @patch.object(Logger,'__new__')
    def test_database_init(self,log):
        self.db = database.Database()
        self.assertIsInstance(self.db.global_config,GlobalConfig._GlobalConfig)
        self.assertTrue(log.called)

    @patch.object(Logger,'__new__')
    def test_database_create_default_database(self,log):
        self.db = database.Database()
        self.db.create_default_database()
        self.validator = datavalidator.DataValidator()
        # check that the directory exists
        self.assertTrue(os.path.isdir(os.getcwd() + self.test_db_dir))
        # check that the database file exists
        self.assertTrue(os.path.isfile(os.getcwd() + self.test_db_file))
        # get the table names from the database
        schema_table_list = self.validator.get_tables()
        # get the user defined tables from the configuration file
        config_table_list = util.get_config_table_list(self.gci.get_ports(),
                                                       self.gci.get_plugin_dictionary())
        # check that the non user defined table p0f exists
        self.assertTrue('p0f' in schema_table_list)
        # check that the non user defined table ipInfo exists
        self.assertTrue('ipInfo' in schema_table_list)
        # check that the non user defined table sessions exists
        self.assertTrue('sessions' in schema_table_list)
        # check that the user defined tables are a subset of the tables in the database schema
        self.assertTrue(set(config_table_list) < set(schema_table_list))
        shutil.rmtree(os.getcwd() + self.test_db_dir)

    @patch.object(Logger,'__new__')
    def test_database_create_db_dir(self,log):
        self.db = database.Database()
        self.db.create_db_dir()
        self.assertTrue(os.path.isdir(os.getcwd() + self.test_db_dir))
        self.assertTrue(log.called)
        shutil.rmtree(os.getcwd() + self.test_db_dir)

    @patch.object(Logger,'__new__')
    def test_database_create_db_dir_already_exists(self,log):
        os.mkdir(os.getcwd() + self.test_db_dir)
        self.assertTrue(os.path.isdir(os.getcwd() + self.test_db_dir))
        self.db = database.Database()
        log.reset_mock()
        self.db.create_db_dir()
        self.assertFalse(log.called)
        shutil.rmtree(os.getcwd() + self.test_db_dir)

    @patch.object(Logger,'__new__')
    def test_database_create_db(self,log):
        self.db = database.Database()
        self.db.create_db_dir()
        self.db.create_db()
        self.assertTrue(os.path.isfile(os.getcwd() + self.test_db_file))
        self.assertTrue(log.called)
        shutil.rmtree(os.getcwd() + self.test_db_dir)

    @patch.object(Logger,'__new__')
    def test_database_update_schema(self,log):
        self.db = database.Database()
        self.db.create_db_dir()
        self.db.create_db()
        util.run_db_scripts(self.gci)
        self.db.update_schema()
        self.validator = datavalidator.DataValidator()
        schema = self.validator.get_schema()

        self.assertTrue(schema['test_http'][5][1] == 'command')
        self.assertTrue(schema['test_http2'][6][1] == 'path')
        self.assertTrue(len(schema['test_telnet']) == 7)

        # set global config instance to the differing column config file
        self.gci = GlobalConfig(self.plugins_config_diff_file,self.global_config_file,True)
        self.gci.read_global_config()
        self.gci.read_plugin_config()

        self.db2 = database.Database()
        self.db2.update_schema()
        self.validator2 = datavalidator.DataValidator()

        schema2 = self.validator2.get_schema()

        self.assertTrue(schema2['test_http'][5][1] == 'unit_test_data_1')
        self.assertTrue(schema2['test_http2'][6][1] == 'unit_test_data_2')
        self.assertTrue(len(schema2['test_telnet']) == 8)
        self.assertTrue(schema2['test_telnet'][7][1] == 'unit_test_data_3')

        # set global config instance back to normal
        self.gci = GlobalConfig(self.plugins_config_file,self.global_config_file,True)
        self.gci.read_global_config()
        self.gci.read_plugin_config()

        shutil.rmtree(os.getcwd() + self.test_db_dir)

















import unittest
from database import database
from database import Table_Insert
from database import datavalidator
from database import util
from common.globalconfig import GlobalConfig
from unittest.mock import patch
from common.logger import Logger
import sqlite3
import os
import shutil

class Table_Insert_test(unittest.TestCase):

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
        self.telnet_data = {'test_telnet':{'session':'abcdefghijklmnop','eventDateTime':'01-02-2016 11:22:33.123',
                                           'peerAddress':'24.33.21.123', 'localAddress':'192.168.0.55',
                                           'input_type':'a string','user_input':'another string'}}
        self.telnet_data_noip = {'test_telnet':{'session':'abcdefghijklmnop','eventDateTime':'01-02-2016 11:22:33.123',
                                           'input_type':'a string','user_input':'another string'}}

    @patch.object(Logger,'__new__')
    def test_telnet_all_values(self,log):
        db = database.Database()
        db.create_default_database()
        validator = datavalidator.DataValidator()
        Table_Insert.prepare_data_for_insertion(validator.get_schema(), self.telnet_data)
        connection = sqlite3.connect(self.gci['Database']['path'])
        cursor = connection.cursor()
        row = cursor.execute('select * from test_telnet;').fetchall()[0]
        check_list = self.helper_get_values_out(self.telnet_data)
        self.assertTrue(set(row) > set(check_list))
        shutil.rmtree(os.getcwd() + self.test_db_dir)

    @patch.object(Logger,'__new__')
    def test_telnet_missing_non_required_values(self,log):
        db = database.Database()
        db.create_default_database()
        validator = datavalidator.DataValidator()
        Table_Insert.prepare_data_for_insertion(validator.get_schema(), self.telnet_data_noip)
        connection = sqlite3.connect(self.gci['Database']['path'])
        cursor = connection.cursor()
        row = cursor.execute('select * from test_telnet;').fetchall()[0]
        check_list = self.helper_get_values_out(self.telnet_data_noip)
        bad_check_list = self.helper_get_values_out(self.telnet_data)
        self.assertTrue(set(row) > set(check_list))
        self.assertFalse(set(row) > set(bad_check_list))
        shutil.rmtree(os.getcwd() + self.test_db_dir)

    def helper_get_values_out(self,dictionary):
        inner_dict = dictionary[util.get_first_key_value_of_dictionary(dictionary)]
        list = []
        for item in inner_dict:
            list.append(inner_dict[item])
        return list

if __name__ == "__main__":
    unittest.main()
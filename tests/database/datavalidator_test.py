import unittest
from database import database
from database import datavalidator
from common.globalconfig import GlobalConfig
from unittest.mock import patch
from common.logger import Logger
import os
import shutil
from database import util

class datavalidator_test(unittest.TestCase):

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
        self.tables_test = ['p0f', 'ipInfo', 'sessions', 'test_http', 'test_http2', 'test_telnet']
        self.table_schema_test = {'sessions': [(0, 'session', 'TEXT', 0, None, 1),
                                               (1, 'table_name', 'TEXT', 1, None, 2)],
                                  'test_http2': [(0, 'ID', 'INTEGER', 1, None, 1),
                                                 (1, 'session', 'TEXT', 0, None, 0),
                                                 (2, 'eventDateTime', 'TEXT', 0, None, 0),
                                                 (3, 'peerAddress', 'TEXT', 0, None, 0),
                                                 (4, 'localAddress', 'TEXT', 0, None, 0),
                                                 (5, 'command', 'TEXT', 0, None, 0),
                                                 (6, 'path', 'TEXT', 0, None, 0),
                                                 (7, 'headers', 'TEXT', 0, None, 0),
                                                 (8, 'body', 'TEXT', 0, None, 0)],
                                  'test_http': [(0, 'ID', 'INTEGER', 1, None, 1),
                                                (1, 'session', 'TEXT', 0, None, 0),
                                                (2, 'eventDateTime', 'TEXT', 0, None, 0),
                                                (3, 'peerAddress', 'TEXT', 0, None, 0),
                                                (4, 'localAddress', 'TEXT', 0, None, 0),
                                                (5, 'command', 'TEXT', 0, None, 0),
                                                (6, 'path', 'TEXT', 0, None, 0),
                                                (7, 'headers', 'TEXT', 0, None, 0),
                                                (8, 'body', 'TEXT', 0, None, 0)],
                                  'p0f': [(0, 'session', 'TEXT', 1, None, 1),
                                          (1, 'first_seen', 'TEXT', 0, None, 0),
                                          (2, 'last_seen', 'TEXT', 0, None, 0),
                                          (3, 'uptime', 'INTEGER', 0, None, 0),
                                          (4, 'last_nat', 'TEXT', 0, None, 0),
                                          (5, 'last_chg', 'TEXT', 0, None, 0),
                                          (6, 'distance', 'INTEGER', 0, None, 0),
                                          (7, 'bad_sw', 'INTEGER', 0, None, 0),
                                          (8, 'os_name', 'TEXT', 0, None, 0),
                                          (9, 'os_flavor', 'TEXT', 0, None, 0),
                                          (10, 'os_match_q', 'INTEGER', 0, None, 0),
                                          (11, 'http_name', 'TEXT', 0, None, 0),
                                          (12, 'http_flavor', 'TEXT', 0, None, 0),
                                          (13, 'total_conn', 'INTEGER', 0, None, 0),
                                          (14, 'link_type', 'TEXT', 0, None, 0),
                                          (15, 'language', 'TEXT', 0, None, 0)],
                                  'ipInfo': [(0, 'ip', 'TEXT', 1, None, 1),
                                             (1, 'plugin_instance', 'TEXT', 1, None, 2),
                                             (2, 'timestamp', 'TEXT', 1, None, 0),
                                             (3, 'hostname', 'TEXT', 0, None, 0),
                                             (4, 'city', 'TEXT', 0, None, 0),
                                             (5, 'region', 'TEXT', 0, None, 0),
                                             (6, 'country', 'TEXT', 0, None, 0),
                                             (7, 'lat', 'REAL', 0, None, 0),
                                             (8, 'long', 'REAL', 0, None, 0),
                                             (9, 'org', 'TEXT', 0, None, 0),
                                             (10, 'postal', 'TEXT', 0, None, 0)],
                                  'test_telnet': [(0, 'ID', 'INTEGER', 1, None, 1),
                                                  (1, 'session', 'TEXT', 0, None, 0),
                                                  (2, 'eventDateTime', 'TEXT', 0, None, 0),
                                                  (3, 'peerAddress', 'TEXT', 0, None, 0),
                                                  (4, 'localAddress', 'TEXT', 0, None, 0),
                                                  (5, 'input_type', 'TEXT', 0, None, 0),
                                                  (6, 'user_input', 'TEXT', 0, None, 0)]}

    @patch.object(Logger,'__new__')
    def test_get_schema_from_database(self,log):
        # will call the constructor because this calls this method
        db = database.Database()
        db.create_default_database()
        validator = datavalidator.DataValidator()
        self.assertTrue(set(validator.tables) == set(self.tables_test))
        self.assertEquals(validator.table_schema,self.table_schema_test)
        shutil.rmtree(os.getcwd() + self.test_db_dir)

    @patch.object(Logger,'__new__')
    def test_get_tables(self,log):
        db = database.Database()
        db.create_default_database()
        validator = datavalidator.DataValidator()
        self.assertIsInstance(validator.get_tables(),list)
        self.assertTrue(set(validator.get_tables()) == set(self.tables_test))
        shutil.rmtree(os.getcwd() + self.test_db_dir)

    @patch.object(Logger,'__new__')
    def test_get_schema(self,log):
        db = database.Database()
        db.create_default_database()
        validator = datavalidator.DataValidator()
        self.assertIsInstance(validator.get_schema(),dict)
        self.assertEquals(validator.get_schema(),self.table_schema_test)
        shutil.rmtree(os.getcwd() + self.test_db_dir)

    @patch.object(Logger,'__new__')
    def test_check_value_len(self, log):
        good_dict = {'table1':{'col1':'val1','col2':'val2'}}
        bad_dict = {'table1':{'col1':'val1','col2':'val2'},'table2':{'col3':'val3','col4':'val4'}}
        db = database.Database()
        db.create_default_database()
        validator = datavalidator.DataValidator()
        log.error = unittest.mock.Mock()
        log.error.reset_mock()
        self.assertTrue(validator.check_value_len(good_dict))
        self.assertFalse(db.log.error.called)
        self.assertFalse(validator.check_value_len(bad_dict))
        self.assertTrue(db.log.error.called)
        shutil.rmtree(os.getcwd() + self.test_db_dir)

    @patch.object(Logger,'__new__')
    def test_check_value_is_dict(self,log):
        good_dict = {'table1':{'col1':'val1','col2':'val2'}}
        bad_dict = ['im a list']
        db = database.Database()
        db.create_default_database()
        validator = datavalidator.DataValidator()
        log.error = unittest.mock.Mock()
        log.error.reset_mock()
        self.assertTrue(validator.check_value_is_dict(good_dict))
        self.assertFalse(db.log.error.called)
        self.assertFalse(validator.check_value_is_dict(bad_dict))
        self.assertTrue(db.log.error.called)
        shutil.rmtree(os.getcwd() + self.test_db_dir)

    @patch.object(Logger,'__new__')
    def test_check_key_in_dict_string(self,log):
        good_dict = {'table1':{'col1':'val1','col2':'val2'}}
        bad_dict = {1:{'col1':'val1'}}
        db = database.Database()
        db.create_default_database()
        validator = datavalidator.DataValidator()
        log.error = unittest.mock.Mock()
        log.error.reset_mock()
        self.assertTrue(validator.check_key_in_dict_string(good_dict))
        self.assertFalse(db.log.error.called)
        self.assertFalse(validator.check_key_in_dict_string(bad_dict))
        self.assertTrue(db.log.error.called)
        shutil.rmtree(os.getcwd() + self.test_db_dir)

    @patch.object(Logger,'__new__')
    def test_check_key_is_valid_table_name(self,log):
        good_dict = {'test_http':{'col1':'val1','col2':'val2'}}
        bad_dict = {'test_table':{'col1':'val1'}}
        db = database.Database()
        db.create_default_database()
        validator = datavalidator.DataValidator()
        log.error = unittest.mock.Mock()
        log.error.reset_mock()
        self.assertTrue(validator.check_key_is_valid_table_name(good_dict))
        self.assertFalse(db.log.error.called)
        self.assertFalse(validator.check_key_is_valid_table_name(bad_dict))
        self.assertTrue(db.log.error.called)
        shutil.rmtree(os.getcwd() + self.test_db_dir)


    @patch.object(Logger,'__new__')
    def test_check_row_value_is_dict(self,log):
        good_dict = {'test_table':{'col1':'val1','col2':'val2'}}
        bad_dict = {'test_table':'i am not a dictionary'}
        db = database.Database()
        db.create_default_database()
        validator = datavalidator.DataValidator()
        log.error = unittest.mock.Mock()
        log.error.reset_mock()
        self.assertTrue(validator.check_row_value_is_dict(good_dict))
        self.assertFalse(db.log.error.called)
        self.assertFalse(validator.check_row_value_is_dict(bad_dict))
        self.assertTrue(db.log.error.called)
        shutil.rmtree(os.getcwd() + self.test_db_dir)

    @patch.object(Logger,'__new__')
    def test_check_all_col_names_strings(self,log):
        good_dict = {'test_table':{'col1':'val1','col2':'val2'}}
        bad_dict = {'test_table':{1:'val1','string':'val2'}}
        db = database.Database()
        db.create_default_database()
        validator = datavalidator.DataValidator()
        self.assertTrue(validator.check_all_col_names_strings(good_dict))
        self.assertFalse(validator.check_all_col_names_strings(bad_dict))
        shutil.rmtree(os.getcwd() + self.test_db_dir)

    @patch.object(Logger,'__new__')
    def test_check_all_col_exist(self,log):
        good_dict = {'test_http':{'session': 'val1','eventDateTime': 'val2','peerAddress': 'val3',
                                  'localAddress': 'val4','command': 'val5','path': 'val6',
                                  'headers': 'val7','body': 'val8'}}
        bad_dict = {'test_http2':{'session': 'val1','eventDateTime': 'val2','peerAddress': 'val3',
                                  'XYZ': 'val4','command': 'val5','path': 'val6',
                                  'headers': 'val7','body': 'val8'}}
        missing_col = {'test_http':{'session': 'val1','eventDateTime': 'val2','peerAddress': 'val3',
                                    'localAddress': 'val4', 'path': 'val6', 'headers': 'val7', 'body': 'val8'}}
        db = database.Database()
        db.create_default_database()
        validator = datavalidator.DataValidator()
        log.error = unittest.mock.Mock()
        log.error.reset_mock()
        self.assertTrue(validator.check_all_col_exist(good_dict))
        self.assertFalse(db.log.error.called)
        self.assertTrue(validator.check_all_col_exist(missing_col))
        self.assertFalse(db.log.error.called)
        self.assertFalse(validator.check_all_col_exist(bad_dict))
        self.assertTrue(db.log.error.called)
        shutil.rmtree(os.getcwd() + self.test_db_dir)



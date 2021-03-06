import unittest
from database import database
from database import dataqueue
from common.globalconfig import GlobalConfig
from unittest.mock import patch
from common.logger import Logger
import queue
import os
import shutil


class dataqueue_test(unittest.TestCase):

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

    @patch.object(Logger,'__new__')
    def test_dataqueue_init(self,log):
        db = database.Database()
        db.create_default_database()
        dq = dataqueue.DataQueue()
        self.assertIsInstance(dq.dataQueue, queue.Queue)
        shutil.rmtree(os.getcwd() + self.test_db_dir)

    @patch.object(Logger,'__new__')
    def test_insert_into_dataqueue(self,log):
        insert_dict = {'test_telnet':{'session':'abc',
                                      'eventDateTime':'02-03-2016 04:15:37.037',
                                      'peerAddress':'41.26.134.3',
                                      'localAddress':'192.168.0.51',
                                      'input_type':'test',
                                      'user_input':'test input'}}
        insert_dict2 = {'test_telnet':{'session':'abcd',
                                      'eventDateTime':'02-04-2016 04:15:37.037',
                                      'peerAddress':'41.27.234.3',
                                      'localAddress':'192.168.0.42',
                                      'input_type':'test1',
                                      'user_input':'test input1'}}
        db = database.Database()
        db.create_default_database()
        dq = dataqueue.DataQueue()
        self.assertTrue(dq.check_empty())
        dq.insert_into_data_queue(insert_dict)
        self.assertFalse(dq.check_empty())
        dq.insert_into_data_queue(insert_dict2)
        self.assertTrue(dq.dataQueue.qsize() == 2)
        result = dq.get_next_item()
        self.assertTrue(insert_dict, result)
        self.assertTrue(dq.dataQueue.qsize() == 1)
        result2 = dq.get_next_item()
        self.assertTrue(insert_dict2, result2)
        self.assertTrue(dq.check_empty())

        shutil.rmtree(os.getcwd() + self.test_db_dir)

    @patch.object(Logger,'__new__')
    def test_insert_into_dataqueue_bad_value(self,log):
        insert_dict = {'test_telnet':{'session':'abc',
                                      'eventDateTime':'02-03-2016 04:15:37.037',
                                      'peerAddress':'41.26.134.3',
                                      'localAddress':'192.168.0.51',
                                      'input_type':'test',
                                      'user_input':'test input',
                                      'fake_column':'bad data'}}
        db = database.Database()
        db.create_default_database()
        dq = dataqueue.DataQueue()
        self.assertFalse(dq.insert_into_data_queue(insert_dict))

        shutil.rmtree(os.getcwd() + self.test_db_dir)

if __name__ == "__main__":
    unittest.main()
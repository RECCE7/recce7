import unittest
from database import datamanager
from database import dataqueue
from common.globalconfig import GlobalConfig
from unittest.mock import patch
from common.logger import Logger
import os
import shutil


class datamanager_test(unittest.TestCase):

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
    def test_datamanager_init(self,log):
        self.dm = datamanager.DataManager()
        self.assertTrue(os.path.isdir(os.getcwd() + self.test_db_dir))
        self.assertTrue(os.path.isfile(os.getcwd() + self.test_db_file))
        self.assertIsInstance(self.dm.q, dataqueue.DataQueue)
        shutil.rmtree(os.getcwd() + self.test_db_dir)

#    @patch.object(Logger,'__new__')
#    def test_datamanager_run(self,log):
#        self.dm = datamanager.DataManager()
#        self.dm.start()

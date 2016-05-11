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

from common.logger import Logger
from database.dataqueue import DataQueue
from database.database import Database
from database import Table_Insert
from threading import Thread, Condition

__author__ = 'Ben Phillips'



class DataManager(Thread):
    """
    This is the DataManager class, it creates the database, data queue and
    the condition variable for synchronization between it, the framework and
    the plugins
    """
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.db.create_default_database()
        self.q = DataQueue()
        self.condition = Condition()
        self.kill = False
        self.logger = Logger().get('database.datamanager.DataManager')

    def run(self):
        """
        This will insert all data in the queue and then once finished give up
        control of the condition variable
        """
        while not self.kill:
            self.condition.acquire()
            if self.q.check_empty():
                self.condition.wait()

            while not self.q.check_empty():
                value = self.q.get_next_item()
                Table_Insert.prepare_data_for_insertion(
                    self.q.dv.table_schema, value)
                self.condition.notify()
            self.condition.release()

    def insert_data(self, data):
        """
        Synchronously inserts data into the database.

        :param data: A dictionary with a table name as its key and a dictionary
                     of column names and corresponding values as its value.
        """
        self.condition.acquire()
        if self.q.insert_into_data_queue(data):
            self.condition.notify()
        self.condition.release()

    def shutdown(self):
        self.kill = True
        self.condition.acquire()
        self.condition.notify()
        self.condition.release()
        self.join()
        self.logger.debug('Data manager has shut down.')

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

import queue

from common.globalconfig import GlobalConfig
from common.logger import Logger
from database import datavalidator

__author__ = 'Ben Phillips'

class DataQueue:
    def __init__(self):
        self.dataQueue = queue.Queue()
        self.dv = datavalidator.DataValidator()
        self.log = Logger().get('database.dataqueue.DataQueue')
    """we want to check the data here and fail early
        if the data is good then we want to put it in the data queue
        we will want another python script for the validations (datavalidator.py)
        we need to enforce type constraints because the database will not
        see datavalidator.py"""
    def insert_into_data_queue(self, value):
        if not self.dv.run_all_checks(value):
            self.log.error('--> Validation failed! Unable to add data '
                           'into data queue: ' +
                           str(value))
            return False
        try:
            self.dataQueue.put(value)
        except queue.Full as e:
            self.log.critical('Data queue is full!')
        finally:
            return True

    def get_next_item(self):
        item = self.dataQueue.get()
        self.dataQueue.task_done()
        return item

    def check_empty(self):
        result = self.dataQueue.empty()
        return result

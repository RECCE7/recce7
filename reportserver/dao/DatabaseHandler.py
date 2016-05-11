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

__author__ = 'Charlie Mitchell <belmontrevenge@gmail.com>'
'''
This class will take in a request from the webserver, query the Sqlite database,
and return JSON.
'''

import os
import sqlite3

from common.globalconfig import GlobalConfig
from common.logger import Logger
from reportserver.manager import dateTimeUtility


#Made this a class so that the code in the init method was not executed
#until this class was instantiated.

class DatabaseHandler:

    def __init__(self):
        self.global_config = GlobalConfig()
        self.db_path = self.global_config['Database']['path']
        self.log = Logger().get('reportserver.dao.DatabaseHandler.DatabaseHandler')

    # Connect to given database.
    # Defaults to the honeypot db, but another path can be passed in (mainly for testing).
    # Database needs to exist first.
    def connect(self, database_name):
        if (database_name == None):
            database_name = self.db_path

        if not os.path.exists(database_name):
            self.log.error("Database does not exist in path: " + database_name)
            return None
        try:
            conn = sqlite3.connect(database_name)
        except sqlite3.OperationalError as oe:
            self.log.error("****Problem connecting to database*** at: " + database_name)
            self.log.error(oe)
        else:
            return conn

    # Query DB and return JSON
    def query_db(self, query, args=(), one=False, db=None):
        #print ("#debug args are: " +str(args))
        cur = self.connect(db).cursor()
        cur.execute(query, args)
        r = [dict((cur.description[i][0], value) \
                for i, value in enumerate(row)) for row in cur.fetchall()]
        cur.connection.close()
        return (r[0] if r else None) if one else r

    # Unit of Measure could be "weeks", "days", "hours", "minutes".
    # Return all data from the DB within that measure of time as JSON.
    def get_json_by_time(self, portnumber, uom, units):
        begin_date_iso = dateTimeUtility.get_begin_date_iso(uom, units)
        tableName = self.global_config.get_plugin_config(portnumber)['table']
        date_time_field = self.global_config.get_db_datetime_name()

        #  query = query_db("SELECT * FROM %s where (datetime > '%s')" % (tableName, query_date_iso))
        queryString = "SELECT * FROM %s where %s >= '%s' order by id, %s" % (tableName, date_time_field, begin_date_iso, date_time_field)
        #args = (tableName, date_time_field, begin_date_iso)
        self.log.info("queryString is: " + str(queryString))
        #print ("args to use: " + str(args))
        results = self.query_db(queryString)
        self.log.debug("results: " + str(results))

        return results



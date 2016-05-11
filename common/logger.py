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
import logging

__author__ = 'Randy Sorensen <sorensra@msudenver.edu>'


class Logger:
    __instance = None
    class _Logger:
        def __init__(self, log_path, level):
            self._log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            self._log_level = getattr(logging, level)
            self._open_logs = []
            logging.basicConfig(filename=log_path,
                                level=self._log_level,
                                format=self._log_format)

        def get(self, module_name):
            if module_name in self._open_logs:
                return logging.getLogger(module_name)

            logger = logging.getLogger(module_name)
            logger.setLevel(self._log_level)

            log_handler = logging.StreamHandler()
            log_handler.setLevel(self._log_level)

            formatter = logging.Formatter(self._log_format)
            log_handler.setFormatter(formatter)

            logger.addHandler(log_handler)

            self._open_logs.append(module_name)
            return logger

    def __new__(cls, log_path='recce7.log', level='INFO'):
        if not Logger.__instance:
            Logger.__instance = Logger._Logger(log_path, level)
        return Logger.__instance

    def __getattr__(self, item):
        return getattr(Logger.__instance, item)

    def __setattr__(self, item, value):
        return setattr(Logger.__instance, item, value)

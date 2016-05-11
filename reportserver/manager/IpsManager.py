
from common.globalconfig import GlobalConfig
from reportserver.dao.DatabaseHandler import DatabaseHandler
from reportserver.manager import dateTimeUtility
from reportserver.manager import utilities
from common.logger import Logger

class IpsManager:

    # Ips Manager: calls necessary managers and utilities to generate parameters for sql.
    #
    validPortNumbers = ()

    def __init__(self):
        self.g_config = GlobalConfig()
        self.valid_port_numbers = self.g_config.get_ports()
        self.date_time_field = self.g_config.get_db_datetime_name()
        self.log = Logger().get('reportserver.manager.IpsManager.py')


    def get_data(self, ipaddress, uom, unit):
        self.log.info("Retrieving ipaddress data: " + str(ipaddress) + "  uom:  " + str(uom) + " size: " + str(unit))

        port_data = []

        for port in self.valid_port_numbers:
            results = self.get_json_by_ip(port, ipaddress, uom, unit)
            items = utilities.process_data(results)
            port_data.append({port:items})

        port_json = {
            'ipaddress': str(ipaddress),
            'timespan': uom + "=" + str(unit),
            'ports':port_data
        }
        return port_json


    def get_json_by_ip(self, portnumber, ipaddress, uom, units):
        begin_date_iso = dateTimeUtility.get_begin_date_iso(uom, units)
        table_name = self.g_config.get_plugin_config(portnumber)['table']
        date_time_field = self.g_config.get_db_datetime_name()

        #  query = query_db("SELECT * FROM %s where (datetime > '%s')" % (tableName, query_date_iso))
        queryString = "SELECT * FROM %s where %s >= '%s' and peerAddress = '%s' order by id, %s" % (
            table_name, date_time_field, begin_date_iso, ipaddress, date_time_field)
        # args = (tableName, date_time_field, begin_date_iso)
        self.log.info("queryString is: " + str(queryString))
        # print ("args to use: " + str(args))
        results = DatabaseHandler().query_db(queryString)
        self.log.debug("results: " + str(results))

        return results
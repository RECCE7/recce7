from reportserver.manager.IpsManager import IpsManager
from reportserver.manager import utilities
from common.logger import Logger


badIpAddress = {
    'error': 'invalid ipaddress given'}

class IpsServiceHandler():
    def __init__(self):
        self.log = Logger().get('reportserver.manager.IpsServiceHandler.py')

    def process(self, rqst, path_tokens, query_tokens):
        uom = None
        units = None
        self.log.info("processing ipaddress request:" + str(path_tokens) + str(query_tokens))


        try:
            time_period = utilities.validate_time_period(query_tokens)
            uom = time_period[0]
            units = time_period[1]
        except ValueError:
            rqst.badRequest(units)
            return

        if len(path_tokens) == 5:
            ipaddress = path_tokens[4].strip()
            self.log.debug("requested: " + str(ipaddress))
            if ipaddress is not None or ipaddress is not "":
                try:
                    ipaddress = utilities.validate_ipaddress(ipaddress)
                    self.get_ips_data_by_time(rqst, ipaddress, uom, units)
                except ValueError:
                    rqst.badRequest(badIpAddress)
                    return
            elif ipaddress == None or ipaddress == "":
                self.get_ips_data_by_time(rqst, "", uom, units)
            else:
                rqst.badRequest()
                return
        elif len(path_tokens) == 4:
            self.get_ips_list_json(rqst, uom, units)
        else:
            rqst.badRequest()
            return


    def get_ips_data_by_time(self, rqst, ipaddress, uom, units):

        ips_manager = IpsManager()
        addressjsondata = ips_manager.get_data(ipaddress, uom, units)
        if addressjsondata is not None:
            # send response:
            rqst.sendJsonResponse(addressjsondata, 200)
        else:
            rqst.notFound()

    def get_ips_list_json(self, rqst, uom, units):
        response = "{not implemented yet.}"
        rqst.sendJsonResponse(response,200)
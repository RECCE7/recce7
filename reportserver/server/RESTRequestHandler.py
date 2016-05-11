import json
from reportserver.manager import utilities
from http.server import BaseHTTPRequestHandler
from common.globalconfig import GlobalConfig


from reportserver.server.PortsServiceHandler import PortsServiceHandler
from reportserver.server.IpsServiceHandler import IpsServiceHandler
from reportserver.server.WorldmapServiceHandler import WorldmapServiceHandler



notFoundPayload = {}

badRequestPayload = {
    'error': 'invalid analytics request'}


#  Handles the service request, determines what was requested,
#  then returns back response.
#
class RestRequestHandler (BaseHTTPRequestHandler):

    def do_GET(self) :

        path_query_tuple = utilities.get_path_query_tokens(self.path)
        path_tokens = path_query_tuple[0]
        query_tokens = path_query_tuple[1]

        if self.path.startswith("/v1/analytics"):
            if len(path_tokens) >= 4:
                if str(path_tokens[3]) == "ports":
                    PortsServiceHandler().process(self, path_tokens, query_tokens)
                elif str(path_tokens[3]) == "ipaddresses":
                    IpsServiceHandler().process(self, path_tokens, query_tokens)
                elif str(path_tokens[3]) == "worldmap":
                    WorldmapServiceHandler().process(self, path_tokens, query_tokens)
                elif str(path_tokens[3] == ""):
                    self.showIndex()
                else:
                    self.badRequest()
            else:
                self.showIndex()
        else:
            self.notFound()



    def get_full_url_path(self):
        self.g_config = GlobalConfig()
        self.host = self.g_config.get_report_server_host()
        self.port = self.g_config.get_report_server_port()
        full_path = 'http://%s:%s/v1/analytics' % (str(self.host), str(self.port))
        return full_path

    def getIndexPayload(self):
        return  {'links': ['rel: ports, href: ' + self.get_full_url_path() + '/ports',
                           'rel: ipaddresses, href:' + self.get_full_url_path() + '/ipaddresses']}

    def showIndex(self):
        # send response code:
        self.sendJsonResponse(self.getIndexPayload(), 200)

    def notFound(self):
        # send response code:
        self.sendJsonResponse(notFoundPayload,404)

    def badRequest(self, rqstPayload=badRequestPayload):
        # send response code:
        self.sendJsonResponse(rqstPayload,400)

    def sendJsonResponse(self, payload, responseCode):

        # Note:  responseCode must be set before headers in python3!!
        # see this post:
        # http://stackoverflow.com/questions/23321887/python-3-http-server-sends-headers-as-output/35634827#35634827
        json_result = json.dumps(payload)
        self.send_response(responseCode)
        #todo make this configurable for allow-origin
        self.send_header("Access-Control-Allow-Origin","http://localhost:8000")
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(json_result))
        self.end_headers()
        self.flush_headers()

        self.wfile.write(bytes(json_result, "utf-8"))

        self.wfile.flush()

        return

    def sendPngResponse(self, filepath, responseCode):

        # Note:  responseCode must be set before headers in python3!!
        # see this post:
        # http://stackoverflow.com/questions/23321887/python-3-http-server-sends-headers-as-output/35634827#35634827
        f=open(filepath, 'rb')
        self.send_response(responseCode)
        # todo make this configurable for allow-origin
        self.send_header("Access-Control-Allow-Origin", "http://localhost:8000")
        self.send_header('Content-Type', 'image/png')
        #self.send_header('Content-Length', len(json_result))
        self.end_headers()
        self.flush_headers()
        self.wfile.write(f.read())
        self.wfile.flush()
        f.close()

        return





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

import os.path
import sqlite3

have_basemap = True

from common.globalconfig import GlobalConfig
from common.logger import Logger
from reportserver.manager.IpsManager import IpsManager
from reportserver.manager import dateTimeUtility
from reportserver.manager import utilities

try:
    import matplotlib.pyplot as plt
    import pickle
    from PIL import ImageFont
    from PIL import Image
    from PIL import ImageDraw
    from mpl_toolkits.basemap import Basemap
except ImportError as e:
    have_basemap = False
    print(
        'Basemap not found; WorldMap will not be available. Please visit '
        'http://recce7.github.io/ for Basemap installation instructions.')

badIpAddress = {
    'error': 'invalid ipaddress given'}


pickle_file = 'ip_map.pickle'
pickle_bytes = None


def preload_map():
    if not os.path.isfile(pickle_file):
        ip_map = Basemap(projection='robin', lon_0=0, resolution='c')
        ip_map.drawlsmask(ocean_color="#99ccff", land_color="#009900")
        ip_map.drawcountries(linewidth=0.25, color='#ffff00')
        ip_map.drawcoastlines(linewidth=0.25)
        pickle.dump(ip_map, open(pickle_file, 'wb'), -1)
    else:
        ip_map = pickle.load(open(pickle_file, 'rb'))

    global pickle_bytes
    pickle_bytes = pickle.dumps(ip_map, -1)

preload_map()


class WorldmapServiceHandler():
    def __init__(self):
        self.log = Logger().get('reportserver.manager.WorldmapServiceManager.py')
        self.global_config = GlobalConfig()
        self.global_config.read_plugin_config()
        self.global_config.read_global_config()

    def process(self, rqst, path_tokens, query_tokens):
        global have_basemap
        if not have_basemap:
            err_msg = \
                ('<html><head><title>WorldMap</title></head><body>'
                'To enable WorldMap generation, please visit '
                '<a href="https://recce7.github.io/">the documentation</a> and '
                'follow the directions for installing the Basemap library.'
                '</body></html>')
            rqst.send_response(200)

            #todo make this configurable for allow-origin
            rqst.send_header("Access-Control-Allow-Origin","http://localhost:8000")
            rqst.send_header('Content-Type', 'text/html')
            rqst.send_header('Content-Length', len(err_msg))
            rqst.end_headers()
            rqst.flush_headers()

            rqst.wfile.write(bytes(err_msg, "utf-8"))

            rqst.wfile.flush()

            return

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


        if len(path_tokens) >= 5:
            rqst.badRequest()
            return
        else:
            self.construct_worldmap(rqst, uom, units)

    def construct_worldmap(self, rqst, uom, units):
        #call to construct port list
        #find unique ips by port
        #merge the results togoether
        #build the map
        #probably want to look at the PortsServiceHandler.py or IpsServiceHandler.py to follow those patterns.
        ip_map = pickle.loads(pickle_bytes)

        pts = self.get_point_list(uom, units)
        for pt in pts:
            srclat, srclong = pt
            x, y = ip_map(srclong, srclat)
            plt.plot(x, y, 'o', color='#ff0000', ms=2.7, markeredgewidth=1.0)

        plt.savefig('reportserver/worldmap.png', dpi=600)

        img = Image.open('reportserver/worldmap.png')
        draw = ImageDraw.Draw(img)

        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 175)
        draw.text((50, 50), "Unique IP addresses: last %s %s" % (units, uom),
                  (0, 0, 0), font=font)

        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 125)
        draw.text((50, 325), "Total: %s" % (len(pts)),
                  (0, 0, 0), font=font)

        # draw = ImageDraw.Draw(img)
        # draw = ImageDraw.Draw(img)
        img.save("reportserver/worldmap.png")

        rqst.sendPngResponse("reportserver/worldmap.png", 200)

    def get_point_list(self, uom, units):
        begin_date = dateTimeUtility.get_begin_date_iso(uom, units)
        query_string = ('select lat,long '
                        'from ('
                            'select distinct lat,long,timestamp, ip '
                            'from ipInfo '
                            'where lat is not null '
                            'and long is not null '
                            'and datetime(timestamp) > datetime(\'' + begin_date + '\')'
                            ');')
        connection = sqlite3.connect(self.global_config['Database']['path'])
        cursor = connection.cursor()
        return cursor.execute(query_string).fetchall()





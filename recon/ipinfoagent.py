import requests

from common.globalconfig import GlobalConfig
from common.logger import Logger
from datetime import datetime
from threading import Thread


class IPInfoCache:
    __instance = None

    class _IPInfoCache:
        def __init__(self):
            self.config = GlobalConfig()
            self.ip_dict = {}

        def __getitem__(self, addr):
            if addr in self.ip_dict:
                peer_info = self.ip_dict[addr]
                ago = datetime.now() - peer_info['timestamp']
                cache_secs = int(
                    self.config['Framework']['ipinfo.cache_seconds'])
                if ago.total_seconds() < cache_secs:
                    return peer_info
                del self.ip_dict[addr]
            return None

        def __setitem__(self, addr, info):
            self.ip_dict[addr] = info

    def __new__(cls):
        if not IPInfoCache.__instance:
            IPInfoCache.__instance = IPInfoCache._IPInfoCache()
        return IPInfoCache.__instance

    def __getitem__(self, addr):
        return IPInfoCache.__instance[addr]

    def __setitem__(self, addr, value):
        IPInfoCache.__instance[addr] = value

    def __getattr__(self, name):
        return getattr(IPInfoCache.__instance, name)

    def __setattr__(self, name, value):
        return setattr(IPInfoCache.__instance, name, value)


class IPInfoAgent(Thread):
    def __init__(self, peer_address, framework, instance_name):
        super().__init__()
        self.log = Logger().get('recon.ipinfoagent.IPInfoAgent')
        self.peer_address = peer_address
        self.cache = IPInfoCache()
        self.framework = framework
        self.instance_name = instance_name

    def run(self):
        peer_info = self.cache[self.peer_address]
        if not peer_info:
            request_str = 'http://ipinfo.io/' + self.peer_address
            self.log.debug('making REST request to ' + request_str)
            response = requests.get(request_str, timeout=10)
            peer_info = response.json()

            peer_info['timestamp'] = datetime.now()

            if 'loc' in peer_info:
                lat, long = peer_info['loc'].split(',')
                peer_info['lat'] = float(lat)
                peer_info['long'] = float(long)
                del(peer_info['loc'])

            self.cache[self.peer_address] = peer_info
        else:
            self.log.debug('ipinfo.io data for ' +
                           self.peer_address +
                           ' is still cached')

        peer_info['plugin_instance'] = self.instance_name

        self.framework.insert_data({'ipInfo': peer_info})

        self.log.debug('ipinfo.io data for ' +
                       self.peer_address +
                       ': ' +
                       str(peer_info))

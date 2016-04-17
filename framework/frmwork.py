import grp
import os
import pwd
import signal

from importlib import import_module
from common.globalconfig import GlobalConfig
from database.DataManager import DataManager
from framework.networklistener import NetworkListener

__author__ = 'Jesse Nelson <jnels1242012@gmail.com>, ' \
             'Randy Sorensen <sorensra@msudenver.edu>'

class Framework:
    __instance = None

    class __Framework:
        def __init__(self, plugin_cfg_path, global_cfg_path):
            self._global_config = GlobalConfig(plugin_cfg_path, global_cfg_path)
            self._plugin_imports = {}
            self._listener_list= {}
            self._running_plugins_list = []
            self._data_manager = None
            self._shutting_down = False

        def start(self):
            print('RECCE7 starting (pid ' + str(os.getpid()) + ')')
            print('Press Ctrl+C to exit.\n')
            self.set_shutdown_hook()
            if not self.drop_permissions():
                return
            self._global_config.read_plugin_config()
            self._global_config.read_global_config()
            self._data_manager = DataManager(self._global_config)
            self._data_manager.start()
            self.start_listeners()

        @staticmethod
        def drop_permissions():
            if os.getuid() != 0:
                return True

            dist_name = os.getenv('RECCE7_OS_DIST')
            users_dict = {'centos': ('nobody', 'nobody'),
                          'debian': ('nobody', 'nogroup')}
            if dist_name not in users_dict:
                print(
                    'Unable to lower permission level - not continuing as\n'
                    'superuser. Please set the environment variable\n'
                    'RECCE7_OS_DIST to one of:\n\tcentos\n\tdebian\n'
                    'or rerun as a non-superuser.')
                return False
            lowperm_user = users_dict[dist_name]
            nobody_uid = pwd.getpwnam(lowperm_user[0]).pw_uid
            nogroup_gid = grp.getgrnam(lowperm_user[1]).gr_gid

            os.setgroups([])
            os.setgid(nogroup_gid)
            os.setuid(nobody_uid)
            os.umask(0o077)

            return True

        def create_import_entry(self, port, name, clsname):
            imp = import_module('plugins.' + name)
            self._plugin_imports[port] = getattr(imp, clsname)

        def start_listeners(self):
            ports = self._global_config.get_ports()
            for port in ports:
                print('Listener started on port: ' + str(port))
                plugin_config = self._global_config.get_plugin_config(port)
                module = plugin_config['module']
                clsname = plugin_config['moduleClass']
                self.create_import_entry(port, module, clsname)
                listener = NetworkListener(plugin_config, self)
                listener.start()
                self._listener_list[port] = listener

        def set_shutdown_hook(self):
            signal.signal(signal.SIGINT, self.shutdown)

        def shutdown(self, *args):
            self._shutting_down = True

            print("Shutting down network listeners")
            for listener in self._listener_list.values():
                listener.shutdown()

            print("Shutting down plugins")
            for plugin in self._running_plugins_list:
                plugin.shutdown()

            print("Shutting down data manager")
            self._data_manager.shutdown()

            print("Goodbye.")

        #
        # Framework API
        #

        '''
        Returns the configuration dictionary for the plugin
        running on the specified port.

        :param port: a port number associated with a loaded plugin
        :return: a plugin configuration dictionary
        '''
        def get_config(self, port):
            return self._global_config.get_plugin_config(port)

        '''
        Spawns the plugin configured by 'config' with the provided
        (accepted) socket.

        :param socket: an open, accepted socket returned by
                       socket.accept()
        :param config: the plugin configuration dictionary describing
                       the plugin to spawn
        :return: a reference to the plugin that was spawned
        '''
        def spawn(self, socket, config):
            # ToDo Throw exception if plugin class not found
            plugin_class = self._plugin_imports[config['port']]
            plugin = plugin_class(socket, config, self)
            plugin.start()
            self._running_plugins_list.append(plugin)
            return plugin

        '''
        Inserts the provided data into the data queue so that it can
        be pushed to the database.

        :param data: data object to add to the database
        '''
        def insert_data(self, data):
            self._data_manager.insert_data(data)

        '''
        Tells the framework that the specified plugin has stopped
        running and doesn't need to be shutdown explicitly on program
        exit.

        :param plugin: a reference to a plugin
        '''
        def plugin_stopped(self, plugin):
            if self._shutting_down:
                return

            self._running_plugins_list.remove(plugin)

    def __new__(cls, plugin_cfg_path, default_cfg_path):
        if not Framework.__instance:
            Framework.__instance = Framework.__Framework(
                plugin_cfg_path, default_cfg_path)
        return Framework.__instance

    def __getattr__(self, name):
        return getattr(Framework.__instance, name)

    def __setattr__(self, name, value):
        return setattr(Framework.__instance, name, value)


default_plugin_cfg_path = 'config/plugins.cfg'
default_global_cfg_path = 'config/global.cfg'

def main():
    plugin_cfg_path = \
        os.getenv('RECCE7_PLUGIN_CONFIG') or default_plugin_cfg_path
    global_cfg_path = \
        os.getenv('RECCE7_GLOBAL_CONFIG') or default_global_cfg_path

    framework = Framework(plugin_cfg_path, global_cfg_path)
    framework.start()

if __name__ == '__main__': main()

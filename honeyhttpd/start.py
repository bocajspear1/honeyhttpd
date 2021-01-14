"""
.. module:: start
   :platform: Unix
   :synopsis: Main module for HoneyHTTPd. Starts servers.

.. moduleauthor:: Jacob Hartman <jacob@j2h2.com>

"""

import sys
import argparse
import time
import os
import json
import pwd
import grp
from termcolor import colored


if sys.version_info.major == 2:
    from Queue import Queue
else:
    from queue import Queue

from .lib.module_util import import_module


VERSION = "v0.5.2"

BANNER = """
        _______  _        _______                   __________________ _______  ______  
|\     /|(  ___  )( (    /|(  ____ \|\     /||\     /|\__   __/\__   __/(  ____ )(  __  \ 
| )   ( || (   ) ||  \  ( || (    \/( \   / )| )   ( |   ) (      ) (   | (    )|| (  \  )
| (___) || |   | ||   \ | || (__     \ (_) / | (___) |   | |      | |   | (____)|| |   ) |
|  ___  || |   | || (\ \) ||  __)     \   /  |  ___  |   | |      | |   |  _____)| |   | |
| (   ) || |   | || | \   || (         ) (   | (   ) |   | |      | |   | (      | |   ) |
| )   ( || (___) || )  \  || (____/\   | |   | )   ( |   | |      | |   | )      | (__/  )
|/     \|(_______)|/    )_)(_______/   \_/   |/     \|   )_(      )_(   |/       (______/ 
                                                                                        
"""

class ServerManager(object):

    def __init__(self, config_file_path):
        self._servers = []
        self._config = {}
        self.parse_config(config_file_path)
        self.__loggers = []
        self.setup_loggers()

    def setup_loggers(self):
        """
        .. function:: setup_loggers(self)

        Sets up the configured loggers

        """
        for item in self._config['loggers']:

            if self._config['loggers'][item]['active'] == False:
                continue

            logger_module = import_module("honeyhttpd/loggers", item)
            if logger_module is None:
                self.error("Invalid handler " + item)
                sys.exit(2)

            if "config" in self._config['loggers'][item]:
                self.__loggers.append(logger_module(self._config['loggers'][item]['config']))
            else:
                self.__loggers.append(logger_module())

        if len(self.__loggers) == 0:
            print("No loggers configured")
            sys.exit(1)


    def start_servers(self):

        # Prepare to start the servers
        server_list = self._config['servers']

        server_count = len(server_list)
        self.notice("Starting " + str(server_count) + " servers\n")
        wait = Queue(maxsize=server_count)

        # Add servers
        for server_config in server_list:
            handler = server_config['handler']
            server_module = import_module("servers", handler)
            if server_module is None:
                self.error("Invalid handler " + handler)
                sys.exit(2)

            server = None
            
            if server_config['mode'] == "http":
                print("Starting http on port " + str(server_config['port']))
                server = server_module(server_config['domain'], int(server_config['port']), server_config['timeout'], wait, self.__loggers)
            elif server_config['mode'] == "https":
                if "cert_path" not in server_config:
                     self.error("cert_path not set for https " + handler)
                     sys.exit(3)
                print("Starting https on port " + str(server_config['port']))
                server = server_module(server_config['domain'], int(server_config['port']), server_config['timeout'], wait, self.__loggers, server_config['cert_path'])

            server.start()
            self._servers.append(server)

        # Wait until they indicate they have bound
        while not wait.full():
            pass

        wait = None

        # Drop privileges
        self.drop_privileges()

        # Wait until told to exit
        try:
            while True:
                time.sleep(2) 
        except KeyboardInterrupt:
            print("\nShutting down...")
            # for server in self._servers:
            #     server.stop()
            #     server.join()
            sys.exit(0)

    def drop_privileges(self):
        
        if os.geteuid() != 0 and os.getegid() != 0:
            return
        
        nobody_uid = pwd.getpwnam(self._config['user']).pw_uid
        nobody_gid = grp.getgrnam(self._config['group']).gr_gid
        self.notice("Dropping Privileges!")

        os.setgroups([])

        os.setgid(nobody_uid)
        os.setuid(nobody_gid)

    def parse_config(self, config_file_path):
        if not os.path.exists(config_file_path):
            self.error("Config file does not exist")
            sys.exit(1)

        config_data = open(config_file_path, "r").read()
        config = json.loads(config_data)

        config_items = ['servers', 'user', 'group', 'loggers']

        for item in config_items:
            if item not in config:
                self.error("Invalid config, '" + item + "' key not found")
                sys.exit(1)
        
        self._config = config

    def notice(self, message):
        print(colored("[*] " + message, "cyan"))

    def error(self, message):
        print(colored("[!] " + message, "red"))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Pretend to be any almost any HTTP server or service you want')
    parser.add_argument('--config', help='Path to configuration file', required=True)

    args = parser.parse_args()
    config_file_path = args.config


    print(colored(BANNER, 'yellow'))
    print("Welcome to HoneyHTTPd " + VERSION + "\n")

    manager = ServerManager(config_file_path)
    manager.start_servers()

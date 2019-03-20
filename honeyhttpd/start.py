"""
.. module:: start
   :platform: Unix
   :synopsis: Main module for HoneyHTTPd. Starts servers.

.. moduleauthor:: Jacob Hartman <jacob@j2h2.com>

"""
# TODO: this module must be transformed into a web shell

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
    """
        Manage server istances
    """
    def __init__(self, config_file_path):
        self._servers = []  # instance of server running on machine
        self._config = {}   # global configuration maybe for every server istance
        self.parse_config(config_file_path)
        self.__loggers = [] # type of logger enables
        print(colored(BANNER, 'yellow'))
        print("Welcome to HoneyHTTPd " + VERSION + "\n")
        #self.setup_loggers()

    def setup_loggers(self):
        """
            Sets up the configured loggers
            @param : None
            @return : None
        """
        for item in self._config['loggers']:
            # verify active log that must be start
            if self._config['loggers'][item]['active'] == False:
                continue
            # if logger is active so try to load it dinamically
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

    def get_active_server_config(self, cfg):
        """
            Return active server configurations
            @param cfg: server config json obj
            @return : server config
        """
        active_cfg = {}
        for c,v in cfg.items():
            if v == "":
                continue
            active_cfg[c] = v
        return active_cfg
        
    def start_servers(self):
        """
            Start server with right configuration 
            @param : None
            @return : None
        """
        server_list = self._config['servers']
        # Server istance
        server = None
        # number of server started
        server_count = len(server_list)

        self.notice("Starting " + str(server_count) + " servers\n")

        wait = Queue(maxsize=server_count)

        for server_config in server_list:
            server_module = import_module("servers", server_config["handler"])
            if server_module is None:
                self.error("Invalid handler " + server_config["handler"])
                sys.exit(2)
            config = server_config["config"]
            # FIXME : Devo convertire in tupla server_address
            if config["mode"] == "http":
                print("Starting http on port " + str(config['server_address'][1]))
                server = server_module(**self.get_active_server_config(config))
            else:
                certificate = config["cert_path"]
                if certificate is None:
                    self.error("cert_path not set for https " + server_config["handler"])
                    sys.exit(3)
                print("Starting https on port " + str(config['server_address'][1]))
                server = server_module(**self.get_active_server_config(config))
            # Register running server istance
            self.update_server_istance(server)
            self.check_server_istance()
            print("[**] Server manager is going to shutdown now ...")
 
    def drop_privileges(self):
        """
            Remove root privileges
            @param : None
            @return : None
        """
        
        if os.geteuid() != 0 and os.getegid() != 0:
            return
        
        nobody_uid = pwd.getpwnam(self._config['user']).pw_uid
        nobody_gid = grp.getgrnam(self._config['group']).gr_gid
        self.notice("Dropping Privileges!")

        os.setgroups([])

        os.setgid(nobody_uid)
        os.setuid(nobody_gid)

    def parse_config(self, config_file_path):
        """
            Get file configurations
            @param config_file_path: path of configuration file
            @return : None
        """
        if not os.path.exists(config_file_path):
            self.error("Config file does not exist")
            sys.exit(1)

        config_data = open(config_file_path, "r").read()
        config = json.loads(config_data)

        # check if configuration file is it ok and this is the right structure
        config_items = ['servers', 'user', 'group', 'loggers']

        for item in config_items:
            if item not in config:
                self.error("Invalid config, '" + item + "' key not found")
                sys.exit(1)
        # little fix for server_address value that must be 
        #config["servers"]["config"]["server_address"] = tuple(config["servers"]["config"]["server_address"])
        
        self._config = config

    def update_server_istance(self, s):
        """
            Update active server istance
            @param s: server istance
            @return : None
        """
        self._servers.append(s)

    def check_server_istance(self):
        """
            Terminate server manager when all of server istances are destroyed
            @ return : None
        """
        try:
            while True:
                if len(self._servers) == 0:
                    self.notice("Seams that all server instace has been destroyed\nDropping privileges...")
                    break
        except KeyboardInterrupt:
            self.error("Manual interrupt generated")
        finally:
            self.drop_privileges()
        
    def notice(self, message):
        print(colored("[*] " + message, "cyan"))

    def error(self, message):
        print(colored("[!] " + message, "red"))



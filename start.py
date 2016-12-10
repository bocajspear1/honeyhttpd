import sys
import argparse
import time
import os
import json
import pwd
import grp
from termcolor import colored

import util.module_util as module_util

if sys.version_info.major == 2:
    from Queue import Queue
else:
    from queue import Queue


# from loggers.elasticsearch_logger import ElasticSearchLogger
# from loggers.file_logger import FileLogger

VERSION = "v0.5"

class ServerManager(object):

    def __init__(self, config_file_path):
        self._servers = []
        self._config = {}
        self.parse_config(config_file_path)
        self.__loggers = []
        # self.setup_loggers()

    # def setup_loggers(self):
    #     valid_loggers = ['elasticsearch', 'file']
    #     for item in self._config['loggers']:

    #         if self._config['loggers'][item]['active'] == False:
    #             continue

    #         if item == 'elasticsearch':
    #             self.__loggers.append(ElasticSearchLogger(self._config['loggers'][item]['config']))
    #         elif item == "file":
    #             self.__loggers.append(FileLogger())
    #         else:
    #             print("Invalid logger")
    #             sys.exit(1)

    #     if len(self.__loggers) == 0:
    #         print("No loggers configured")
    #         sys.exit(1)


    def start_servers(self):

        # Prepare to start the servers
        server_list = self._config['servers']

        server_count = len(server_list)
        self.notice("Starting " + str(server_count) + " servers\n")
        wait = Queue(maxsize=server_count)

        # Add servers
        for server_config in server_list:
            handler = server_config['handler']
            server_module = module_util.import_module(handler)
            if server_module is None:
                self.error("Invalid handler " + handler)
                sys.exit(2)

            server = None
            if server_config['mode'] == "http":
                server = server_module(server_config['domain'], int(server_config['port']), server_config['timeout'], wait)
            elif server_config['mode'] == "https":
                if "cert_path" not in server_config:
                     self.error("cert_path not set for https " + handler)
                     sys.exit(3)
                server = server_module(server_config['domain'], int(server_config['port']), server_config['timeout'], wait, server_config['cert_path'])
            
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

parser = argparse.ArgumentParser(description='Look at what attackers are poking web servers with')
parser.add_argument('--config', help='Path to configuration file', required=True)

args = parser.parse_args()
config_file_path = args.config

banner = """
          _______  _        _______                   __________________ _______  ______  
|\     /|(  ___  )( (    /|(  ____ \|\     /||\     /|\__   __/\__   __/(  ____ )(  __  \ 
| )   ( || (   ) ||  \  ( || (    \/( \   / )| )   ( |   ) (      ) (   | (    )|| (  \  )
| (___) || |   | ||   \ | || (__     \ (_) / | (___) |   | |      | |   | (____)|| |   ) |
|  ___  || |   | || (\ \) ||  __)     \   /  |  ___  |   | |      | |   |  _____)| |   | |
| (   ) || |   | || | \   || (         ) (   | (   ) |   | |      | |   | (      | |   ) |
| )   ( || (___) || )  \  || (____/\   | |   | )   ( |   | |      | |   | )      | (__/  )
|/     \|(_______)|/    )_)(_______/   \_/   |/     \|   )_(      )_(   |/       (______/ 
                                                                                          
"""

print(colored(banner, 'yellow'))
print("Welcome to HoneyHTTPd " + VERSION + "\n")

manager = ServerManager(config_file_path)
manager.start_servers()

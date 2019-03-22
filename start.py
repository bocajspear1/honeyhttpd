import argparse
from honeyhttpd.start import ServerManager
import os
from termcolor import colored


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Look at what attackers are poking web servers with')
    parser.add_argument('--config', help='Path to configuration file', required=True)

    args = parser.parse_args()
    config_file_path = args.config
    """
    if os.geteuid() != 0 and os.getegid() != 0:
        print(colored("[!] Root privileges are required", "red"))
    else:
        manager = ServerManager(config_file_path)
        manager.start_servers()
    """
    manager = ServerManager(config_file_path)
    manager.start_servers()

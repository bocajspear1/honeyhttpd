import argparse
from termcolor import colored
from honeyhttpd.start import ServerManager, VERSION, BANNER


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Look at what attackers are poking web servers with')
    parser.add_argument('--config', help='Path to configuration file', required=True)

    args = parser.parse_args()
    config_file_path = args.config

    print(colored(BANNER, 'yellow'))
    print("Welcome to HoneyHTTPd " + VERSION + "\n")

    manager = ServerManager(config_file_path)
    manager.start_servers()

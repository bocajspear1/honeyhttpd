# HoneyHTTPD

![HoneyHTTPD Logo](honeyhttpd.png)

HoneyHTTPD is a Python-based web server framework. It makes it easy to set up fake web servers and web services, respond with the precise data you want, and record the requests given to it. HoneyHTTPD allows you to build your responses with Python at the HTTP protocol level to imitate almost any server or service you want. No complex setups and proxies required!

This information can be logged to different places, the currently supported outputs are:
* Files
* ElasticSearch
* Stdout
* AWS S3

HoneyPoke supports both Python 2.7 (I know its EOL, but just in case) and Python 3.

## Installation

1. Clone or download this repo
2. Install dependencies: 
    * Python 2: `sudo pip install -r requirements.txt` 
    * Python 3: `sudo pip3 install -r requirements.txt` 
3. Be sure the `large` and `logs` directories are writeable by the user and group you plan to have HoneyHTTPD running under.

## Setup

1. Copy `config.json.default`  to `config.json` Modify the config file. 
    * `loggers` enables and disables loggers. This done with the `active` key under the respective loggers. Some may need extra configuation, which is in the `config` key.
    * `servers` contains a list of servers you want to run. Each entry has the following keys:
        * `handler` indicates the server module in the `servers` directory to use for that port
        * `mode` is either `http` or `https` which indicates if the server should return normal HTTP or HTTPS
        * `port` is the port to run on 
        * `domain` indicates the "domain" this server is running 
        * `timeout` is the timeout for requests 
        * `cert_path` is only required when in `https` mode. This is the path to the server certificate in the PEM format.
    * `user` is the user you want the script to drop privileges to
    * `group` is the group you want the script to drop privileges to
2. Run HoneyHTTPD with:
    * Python 2 `sudo python2 start.py --config config.json`
    * Python 3 `sudo python3 start.py --config config.json`

## Making Server Modules

Server modules live in the `servers` directory. They are classes that handle the HTTP requests. These modules must inherit from the `Server` class in `lib.server`. The class name and the name of the server module file must be the same. Modules can inherit from other server modules to build on their functionality.

## Generating SSL certificates

```
openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
```

From [here](https://gist.github.com/dergachev/7028596).

## Contributing

Go at it! Open an issue, make a pull request, fork it, etc.

## License

This project is licensed under the Mozilla Public License, v2.0 (formerly GPL 3.0)

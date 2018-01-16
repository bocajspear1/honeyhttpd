Documentation for HoneyHTTPd
======================================

Welcome to the documentation for HoneyHTTPd, a Python HTTP honeypot framework.

HoneyHTTPd's goal is to make creating fake HTTP services as simple and fast as possible.


Getting Started
*********************************

The easiest way to get started is to get or build some server modules, and use ``start.py`` to run them.

Server modules are Python modules that are stored in a directory named ``servers`` in the same directory you execute from.

The file structure looks like this: ::

    honeyhttpd/
    servers/
        ApacheServer.py
    start.py
    ..

A config file is also required. A sample one is below (or in ``config.json.default`` if you got the code from GitHub) ::

    {
        "loggers": {
            "elasticsearch": {
                "active": false,
                "config": {
                    "server": "http://USERNAME:PASSWORD@ELASTICSEARCH_SERVER",
                    "verify": false
                }
            }, 
            "file": {
                "active": true
            }
        },
        "servers" : [
            {"handler": "ApacheServer", "mode": "https", "port": 8443, "domain": "example.com", "timeout": 10, "cert_path": "server.pem"},
            {"handler": "ApacheServer", "mode": "http", "port": 8000, "domain": "example.com", "timeout": 10}
        ],
        "user": "nobody",
        "group": "nogroup"
    }


This should get you started.

Making Your Own Server Modules
*********************************

Server Modules are simply Python modules that inherit from the ``Server`` class in ``honeyhttpd.lib.server``. These modules are placed in the ``servers`` directory.

The module details are as follows: 

.. autoclass:: honeyhttpd.lib.server.Server
    :members:
    :undoc-members:
    :show-inheritance:  
    :noindex:


More Info
==================

.. toctree::
    :maxdepth: 1

    modules


Module Details and Search
*****************************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`




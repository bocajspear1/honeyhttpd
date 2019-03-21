"""
    Author : Cavallo Luigi
    Info   : fork of https://github.com/bocajspear1 project named honeypothttpd
"""

from socketserver import ThreadingTCPServer, TCPServer  # for TCPServer type
import sys                                              # for system command
import os                                               # for file operations
from ssl import SSLContext                              # for secure sock
from datetime import datetime                           # for current datetime

# Backword compatibility with python 2.x
if sys.version_info.major == 2:
    from BaseHTTPServer import BaseHTTPRequestHandler
else:
    from http.server import BaseHTTPRequestHandler


class BaseHandler(BaseHTTPRequestHandler):
    """
        Base handler for in-come requests.
        -> self.command   => GET/POST/PUT/DELETE/HEAD
        -> self.path      => / or /index.html
        -> self.request_version   => HTTP/1.1
        TODO: Manage header
    """
    # Must be overrided in other server instance
    server_version = "Apache/2.4"

    def do_GET(self):
        """
            Management of GET requests.
            ****
            Must be extended.
            ****
        """
        print("[%s:%d] => %s %s %s %s" %(self.client_address[0], self.client_address[1], 
                                        self.command, self.path, self.request_version, datetime.now()))

    def do_POST(self):
        """
            Management of POST requests.
            ****
            Must be extended.
            ****
        """
        self.send_response(505, message="Internal Server Error")

    def server_version(self):
        """ 
            Print server_version.
            Es. Apache/Tomcat ecc..
        """
        return self.server_version


class Server(TCPServer):
    """ 
        TODO: Implement https wrapper
        TODO: link the login 
        TODO: Redefine instance variables as private and create 
              properties to access them safely
        TODO: Adding security check for methods e some instance attribute
    """
    allow_reuse_address = True
    
    def __init__(self, server_address, loggers="", RequestHandlerClass=BaseHandler, bind_and_activate=True, mode="http",
                 cert_path=None, timeout=None):
        super().__init__(tuple(server_address), RequestHandlerClass, bind_and_activate)
        # Loggers type
        self.log = loggers
        # http or https server
        self.mode = mode
        # timeout definition
        self.timeout = timeout
        # Only for https certificate 
        self.cert_path = cert_path
        # https logic 
        if self.cert_path is not None:
            if os.path.exists(self.cert_path):
                self.ctx = SSLContext()
                self.ctx.load_cert_chain(certfile=self.cert_path)
                self.socket = SSLContext.wrap_socket(self.ctx, sock=self.socket, server_side=True)
            else:
                # TODO : This instance must be eliminated from server's instance
                raise OSError("[!] Certification path error")
        # Start server
        self.serve_forever()

    def server_activate(self):
        print("[*] Server is now active on %s:%d" % (self.server_address[0], self.server_address[1]))
        super().server_activate()

    def startup_logger(self):
        """
            Initialize the logger type
        """
        pass
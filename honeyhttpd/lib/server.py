"""
    Author : Cavallo Luigi
    Info   : fork of https://github.com/bocajspear1 project named honeypothttpd
"""

from socketserver import ThreadingTCPServer, TCPServer  # for TCPServer type
from socketserver import StreamRequestHandler           # for handle requests
import os                                               # for file operations
from ssl import SSLContext                              # for secure sock
from datetime import datetime                           # for current datetime


class BaseHandler(StreamRequestHandler):
    """
        Handler for requests
    """
    def setup(self):
        super().setup()

    def handle(self):
        """
            Must be extended
        :return:
        """
        method, req, proto = self.rfile.readline().strip().decode().split()
        print("[%s:%d] => %s %s %s %s" % (self.client_address[0], self.client_address[1], method, req, proto,
                                         datetime.now()))
        self.wfile.write("\n".encode())

    def finish(self):
        super().finish()


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
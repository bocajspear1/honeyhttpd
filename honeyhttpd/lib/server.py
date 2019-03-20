from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer
import sys 
from datetime import datetime

# Backword compatibility with python 2.x
if sys.version_info.major == 2:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
else:
    from http.server import HTTPServer, BaseHTTPRequestHandler

class BaseHandler(BaseHTTPRequestHandler):
    """
        Handler di base per le richieste in arrivo.
        Le variabili d'instanza più importanti per la gesione del tipo di richliesta sono:
        -> self.command   => GET/POST/PUT/DELETE/HEAD
        -> self.path      => / or /index.html
        -> self.request_version   => HTTP/1.1
        TODO: Ritornare anche un pò di header validi
        TODO: Collegare il logging
    """
    # Must be overrided in other server istance
    server_version = "Apache/2.4"
    def do_GET(self):
        """
            Gestione delle richieste GET.
            ****
            Deve essere sovrascritto per gestire
            la logica di accesso alle risorse
            ****
        """
        print("[%s] => %s %s %s %s" %(self.address_string(), self.command, self.path, self.request_version, datetime.now()))

    def do_POST(self):
        """
            Gestione delle richieste POST.
            ****
            Deve essere sovrascritto per gestire
            la logica di accesso alle risorse
            ****
        """
        self.send_response(505, message="Internal Server Error")

    def server_version(self):
        """ 
            Stampa la versione del server corrente.
            Es. Apache/Tomcat ecc..
        """
        return self.server_version

class Server(TCPServer):
    """ 
        TODO: Gestire https e ssl
        TODO: Collegare il logging
        TODO: Definire bene quali informazioni loggare 
    """
    # Only for devlopment process when in production set to false 
    allow_reuse_address = True
    
    def __init__(self, server_address, loggers="", RequestHandlerClass=BaseHandler, bind_and_activate=True, mode="http", cert_path=None, timeout=None):
        super().__init__(tuple(server_address), RequestHandlerClass, bind_and_activate)
        # Loggers type
        self.log = loggers
        # http or https server
        self.mode = mode
        # timeout definition
        self.timeout = timeout
        # Only for https certificate 
        self.cert_path = cert_path
        # Left https logic here ....
        # ...
        # Start server
        self.serve_forever()

    def server_activate(self):
        print("[*] Server is now active on http://%s:%d" %(self.server_address[0],self.server_address[1]))
        super().server_activate()

    def startup_logger(self):
        """
            Initialize the logger type
        """
        pass

if __name__ == "__main__":
    # For individual testing 
    Server(("localhost", 8080))
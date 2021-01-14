import hashlib
import os
import ssl
import sys
import threading
from string import Template
import copy

from .encode import *

if sys.version_info.major == 2:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from SocketServer import ThreadingMixIn
else:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from socketserver import ThreadingMixIn


# Handler for HTTP requests
class HTTPHandler(BaseHTTPRequestHandler, object):
    """
    This class is the HTTP handler for the built-in Python HTTP server

    """
    def get_raw_request(self):
        """
        This method gets the request as a string

        :returns: (str) The HTTP request as a string

        """
        if self.command is None or self.path is None or self.request_version is None:
            return ""

        raw_request = self.command + " " + self.path + " " + self.request_version + "\n" + str(self.headers)
        
        if "Content-Length" in self.headers:
            length = int(self.headers['Content-Length'])
            if sys.version_info.major == 2:
                raw_request += "\n" + self.rfile.read(length)
            else:
                raw_request += "\n" + self.rfile.read(length).decode('utf-8')

        return raw_request

    # For sending errors (Overwrite)
    def send_error(self, code, extra=""):
        """
        This function is called to send error responses

        :param code: (int) The HTTP status code
        :param extra: (str) Extra data

        """
        message = self.responses[code][0]

        # Call the user's on_error hook
        code, headers, message = self.on_error(code, self.headers.items(), message)
        desc_template = Template(self.responses[code][1])

        

        set_path = ""
        set_method = ""

        if hasattr(self, "path"):
            set_path = self.path
        else:
            set_path = path="/"

        if hasattr(self, "command"):
            set_method = self.command
        else:
            set_method = path="UNKNOWN"

        desc = desc_template.substitute(path=set_path, method=set_method, extra=extra)

        error_template = Template(self.error_message_format)
        error_message = error_template.substitute(description=desc, code=str(code), message=message)

        headers, data = self.response_headers(headers, error_message)
        self.send_response(code, message)
        self.send_header("Content-Length", str(len(data)))
        if code == 302 or code == 301 or code == 307 or code == 308:
            self.send_header("Location", extra)
        elif code == 401:
            self.send_header("WWW-Authenticate", extra)
        for header in headers:
            self.send_header(header[0], header[1]) 
        self.end_headers()

        
        self.wfile.write(data)

        return headers, data

    # For sending responses
    def send_success_response(self, data, headers):

        headers, data = self.response_headers(headers, data)

        self.send_response(200)

        for header in headers:
            self.send_header(header[0], header[1]) 

        self.end_headers()

        
        self.wfile.write(data)

        return headers, data


    # On GET requests
    def do_GET(self):
        
        code, extra = self.on_request(self)
        
        self.server.client_address = self.client_address[0]
        self.server.client_port = self.client_address[1]

        if code != None:
            self.send_error(code, extra)
            return

        req_headers = self.headers.items()
        
        code, headers, data = self.on_GET(self.path, req_headers)

        res_headers = []
        res_data = ""
        
        if code != 200:
            res_headers, res_data = self.send_error(code, data)
        else:
            res_headers, res_data = self.send_success_response(data, headers)

        self.on_complete(self.client_address, code, req_headers, res_headers, self.get_raw_request(), res_data)

    # On POST requests
    def do_POST(self):

        code, extra = self.on_request(self)

        self.server.client_address = self.client_address[0]
        self.server.client_port = self.client_address[1]

        if code != None:
            self.send_error(code, extra)
            return

        req_headers = self.headers.items()

        post_data = ""

        for header in req_headers:
            if header[0] == 'Content-Length':
                try:
                    post_data = self.rfile.read(int(header[1]))
                except:
                    self.send_error(400, "")

        code, headers, data = self.on_POST(self.path, req_headers, post_data)

        res_headers = []
        res_data = ""

        if code != 200:
            res_headers, res_data = self.send_error(code, data)
        else:
            res_headers, res_data = self.send_success_response(data, headers)

        self.on_complete(self.client_address, code, req_headers, res_headers, self.get_raw_request(), res_data)

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

# Main server class. All other servers must inherit from this class
class Server(threading.Thread):
    """
    This class is what all server modules inherit from. It operates as a Python thread (``start()`` to run, etc.).

    .. warning:: The server will not operate while the user or group is root.

    """
    def __init__(self, domain_name, port, timeout, queue, loggers, ssl_cert=None):
        threading.Thread.__init__(self)
        self.daemon = True
        self._domain_name = domain_name
        self._port = port
        self._queue = queue
        self._timeout = timeout
        self._ssl_cert = ssl_cert
        self._loggers = loggers


    # Setup and start the handler
    def run(self):
        """
        This is the main function for the server thread. This will start the actual server process

        """
        server_address = ('', int(self._port))

        # Make a local subclass so we have our own instance of this class
        class MyHandler(HTTPHandler):
            pass

        httpd = ThreadingHTTPServer(server_address, MyHandler)
        httpd.log = self.log
        MyHandler.server_version = self.server_version()
        MyHandler.sys_version = self.system()
        MyHandler.error_message_format = self.error_format(self._port)
        MyHandler.response_headers = self.response_headers
        MyHandler.timeout = self._timeout
        MyHandler.responses = self.responses()

        MyHandler.on_request = self.on_request
        MyHandler.on_GET = self.on_GET
        MyHandler.on_POST = self.on_POST
        MyHandler.on_error = self.on_error
        MyHandler.on_complete = self.on_complete

        if self._ssl_cert is not None:
            httpd.socket = ssl.wrap_socket(httpd.socket, certfile=self._ssl_cert, server_side=True)

        self.ready()

        while os.geteuid() == 0 or os.getegid() == 0:
            pass

        while True:
            httpd.handle_request()

        
    # Set headers for the response
    def response_headers(self, headers, data):
        """
        This method sets the default headers and encodes the data based on the ``Content-Encoding`` header
        if it is set.

        :param headers: (tuple[]) The headers currently set
        :param data: (str) The data
        :returns:  
            * tuple[] - The headers
            * bytes - The encoded data

        """
        for header in self.default_headers():
            headers.append(header)

        content_encoded = False

        for header in headers:
            # Encode the response data if the Content-Encoding is set
            if header[0] == "Content-Encoding":
                content_encoded = True
                if header[1] == "deflate":
                    data = encode_deflate(data)
                elif header[1] == "gzip":
                    data = encode_gzip(data)
                else:
                    data = encode_plain(data)
            # Set the timeout 
            elif header[0] == "Connection" and header[1] == "Keep-Alive":
                headers.append(("Keep-Alive", "timeout=" + str(self._timeout) + ", max=100"))

        headers.insert(0, ("Content-Length", str(len(data))))

        # Ensure the data is encoded
        if not content_encoded:
            data = encode_plain(data)

        return headers, data

    def log(self, client, request, response, extra={}):
        """
        This method records the request and response in the loggers

        :param remote_ip: (str) The remote host's IP address.
        :param remote_port: (int) The remote host's port
        :param request: (str) The string containing the request
        :param response: (str) The string containing the response or message indicating the response
        :param extra: (dict) Extra data to log

        """

        stores_large = True

        for logger in self._loggers:
            stores_large = stores_large and logger.stores_large()

        if stores_large is False and len(request) > 2048:
            large_file = self.save_large_file(client[0], self._port, request)
            request = "Output saved at " + large_file

        for logger in self._loggers:
            logger.log(client[0], client[1], self._ssl_cert is not None, self._port, request, response, extra)

        

    def save_large_file(self, remote_ip, port, data):
        """
        This method saves the data to a file

        :param remote_ip: (str) The remote host's IP address.
        :param port: (int) The remote host's port
        :param data: (str) The data to store in the file

        :returns:  str - The file name where the data is stored

        """
        m = hashlib.md5()
        m.update(data)
        output_filename = "./large/" + remote_ip + "-" + str(port) +  "-" + str(time.time()) + "-" + m.hexdigest() + ".large"

        out_file = open(output_filename, "wb")
        out_file.write(data)
        out_file.close()

        return output_filename

    # Indicate to the main thread that our server is ready
    # This allows us to drop our privileges
    def ready(self):
        """
        Indicates to the main thread that the server is ready to start 

        """
        self._queue.put(True)

    # Return an array or two part tuples
    # e.g. [("key", "value")]
    def default_headers(self):
        """
        .. note:: This function must be implemented

        This method is used to give a list of default headers

        :returns:  list - List of tuples with header data - (KEY, VALUE)

        """
        raise NotImplementedError

# Event methods

    def on_GET(self, path, headers):
        """
        .. note:: This function must be implemented

        This method is called when a GET request is sent to the server
        
        :param path: (str) The path requested.
        :param headers: (tuple[]) The headers passed to the server.
        :returns:  
            * code (int) - HTTP status code

            * headers (str[]) - List containing header
            * data (str) - The return data 

        """
        raise NotImplementedError

    def on_POST(self, path, headers):
        """
        .. note:: This function must be implemented

        This method is called when a POST request is sent to the server
        
        :param path: (str) The path requested.
        :param headers: (tuple[]) The headers passed to the server.
        :returns:  
            * code (int) - HTTP status code
            
            * headers (str[]) - List containing header
            * data (str) - The return data 

        """
        raise NotImplementedError

    def on_request(self, handler):
        """
        .. note:: This function must be implemented

        This method is called when any request is sent to the server
        
        :param handler: The HTTP handler.
        :returns:  
            * code (int) - HTTP status code
            
            * extra (str) - Extra data

        """
        raise NotImplementedError

    def on_error(self, code, headers, message):
        """
        .. note:: This function must be implemented

        This method is called when any non-successful (200) code is returned
        
        :param code: (int) The HTTP status code.
        :param headers: (tuple[]) The HTTP headers to return. Preset with default headers.
        :param message: The message from the ``responses`` method. Variables are filled out.
        :returns:  
            * code (int) - HTTP status code
            
            * headers (str[]) - List containing header
            * data (str) - The return data 

        """
        raise NotImplementedError

    def on_complete(self, client, code, req_headers, res_headers, request, response):
        """
        .. note:: This function must be implemented

        This method is called when any call is completed
        
        :param code: (int) The HTTP status code sent
        :param headers: (tuple[]) The HTTP headers sent
        :param request: The request message
        :param response: The response message
        :returns:  
            None

        """
        raise NotImplementedError

# Server info

    # Return a template string (see Python templates)
    def error_format(self):
        """
        .. note:: This function must be implemented

        This method is used to give the format of error pages.

        The Template string returned can have the following variables:

        * $code - Return code
        * $message - Short message
        * $description - Long message

        :returns:  string -- A Python Template string

        """
        raise NotImplementedError

    def name(self):
        """
        .. note:: This function must be implemented

        :returns:  string -- The name of the server. Used in the config and possibly in the server header

        """
        raise NotImplementedError

    def version(self):
        """
        .. note:: This function must be implemented

        :returns:  string -- The version of the server

        """
        raise NotImplementedError

    def system(self):
        """
        .. note:: This function must be implemented

        :returns:  string -- The system name reported

        """
        raise NotImplementedError

    def server_version(self):
        """
        .. note:: This function must be implemented

        :returns:  string -- The ``Server`` header

        """
        raise NotImplementedError

    def responses(self):
        """
        .. note:: This function must be implemented

        This returns a dict mapping error codes to a tuple of titles and messages. Used in conjunction with ``error_format``

        Dict format is [int] = (string:title, string:message)

        Each message in the response dict can have the following variables:
            * $path - The path of the request
            * $method - The method of the request
            * $extra - An extra string

        :returns:  dict -- Maps error codes to a tuple of title and message. 
            

        """
        raise NotImplementedError

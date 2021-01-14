from honeyhttpd.lib.server import Server

class ApacheServer(Server):

    # Name of the server
    def name(self):
        return "Apache"

    # Version of the server
    def version(self):
        return "2.4.9"

    # The system of the server to fake
    def system(self):
        return "(Ubuntu)"

    # The value placed in the "Server" header
    def server_version(self):
        return self.name() + "/" + self.version()

    # Mapping of HTTP codes to template messages
    def responses(self):
        return {
                200: ('OK', 'Request fulfilled, document follows'), 
                201: ('Created', 'Document created, URL follows'), 
                202: ('Accepted', 'Request accepted, processing continues off-line'), 
                203: ('Non-Authoritative Information', 'Request fulfilled from cache'), 
                204: ('No Content', 'Request fulfilled, nothing follows'), 
                205: ('Reset Content', 'Clear input form for further input.'), 
                206: ('Partial Content', 'Partial content follows.'), 
                400: ('Bad Request', "Your browser sent a request that this server could not understand."), 
                401: ('Unauthorized', "This server could not verify that you\nare authorized to access the document\nrequested.  Either you supplied the wrong\ncredentials (e.g., bad password), or your\nbrowser doesn't understand how to supply\nthe credentials required."), 
                402: ('Payment Required', ''), 
                403: ('Forbidden', "You don't have permission to access $path\non this server."), 
                404: ('Not Found', 'The requested URL $path was not found on this server.'), 
                405: ('Method Not Allowed', "The requested method $method is not allowed for the URL $path."), 
                406: ('Not Acceptable', "An appropriate representation of the requested resource $path could not be found on this server."), 
                407: ('Proxy Authentication Required', "This server could not verify that you\nare authorized to access the document\nrequested.  Either you supplied the wrong\ncredentials (e.g., bad password), or your\nbrowser doesn't understand how to supply\nthe credentials required."), 
                408: ('Request Timeout', "Server timeout waiting for the HTTP request from the client."), 
                409: ('Conflict', ''), 
                410: ('Gone', "The requested resource<br />$path<br />\nis no longer available on this server and there is no forwarding address.\nPlease remove all references to this resource."), 
                411: ('Length Required', "A request of the requested method $method requires a valid Content-length."), 
                412: ('Precondition Failed', "The precondition on the request for the URL $path evaluated to false."), 
                413: ('Request Entity Too Large', "The requested resource<br />$path<br />\ndoes not allow request data with $method requests, or the amount of data provided in\nthe request exceeds the capacity limit."), 
                414: ('Request-URI Too Long', "The requested URL's length exceeds the capacity\nlimit for this server."), 
                415: ('Unsupported Media Type', "The supplied request data is not in a format\nacceptable for processing by this resource."), 
                416: ('Requested Range Not Satisfiable', 'None of the range-specifier values in the Range\nrequest-header field overlap the current extent\nof the selected resource.'), 
                417: ('Expectation Failed', 'Expect condition could not be satisfied.'), 
                423: ('Locked', "The requested resource is currently locked.\nThe lock must be released or proper identification\ngiven before the method can be applied."), 
                424: ('Failed Dependency', "The method could not be performed on the resource\nbecause the requested action depended on another\naction and that other action failed."), 
                426: ('Upgrade Required', "The requested resource can only be retrieved\nusing SSL.  The server is willing to upgrade the current\nconnection to SSL, but your client doesn't support it.\nEither upgrade your client, or try requesting the page\nusing https://\n"), 
                100: ('Continue', 'Request received, please continue'), 
                101: ('Switching Protocols', 'Switching to new protocol; obey Upgrade header'), 
                300: ('Multiple Choices', 'Object has several resources -- see URI list'), 
                301: ('Moved Permanently', "The document has moved <a href=\"$extra\">here</a>."), 
                302: ('Found', "The document has moved <a href=\"$extra\">here</a>."), 
                303: ('See Other', "The document has moved <a href=\"$extra\">here</a>."), 
                304: ('Not Modified', 'Document has not changed since given time'), 
                305: ('Use Proxy', "This resource is only accessible through the proxy\n$extra<br />\nYou will need to configure your client to use that proxy."), 
                307: ('Temporary Redirect', "The document has moved <a href=\"$extra\">here</a>."), 
                500: ('Internal Server Error', "The server encountered an internal error or\nmisconfiguration and was unable to complete\nyour request.</p>\n<p>Please contact the server administrator at \n $extra to inform them of the time this error occurred,\n and the actions you performed just before this error.</p>\n<p>More information about this error may be available\nin the server error log."), 
                501: ('Not Implemented', "$method to $path not supported."), 
                502: ('Bad Gateway', "The proxy server received an invalid\nresponse from an upstream server."), 
                503: ('Service Unavailable', "The server is temporarily unable to service your\nrequest due to maintenance downtime or capacity\nproblems. Please try again later."), 
                504: ('Gateway Timeout', 'The gateway server did not receive a timely response'), 
                505: ('HTTP Version Not Supported', 'Cannot fulfill request.')}

    def default_headers(self):
        return []

    def error_format(self, port):
        return """<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>$code $message</title>
</head><body>
<h1>$message</h1>
<p>$description<br />
</p>\n
<hr>
<address>""" + self.server_version() + " " + self.system() + """ Server at """ + self._domain_name + """ Port """ + str(port) + """</address>
</body></html>

"""

    # Called on any form of request. Return None, None if you wish to continue normally, or return ERROR_CODE, EXTRA
    def on_request(self, handler):
        if not handler.path.startswith("/"):
            return 400, ""
        return None, None

    # Called on GET requests. Return ERROR_CODE, HEADERS, EXTRA
    def on_GET(self, path, headers):
        if path == "/":
            return 426, [], "admin@example.com"
            # return 500, [], "Basic realm=\"test\""
        else:
            return 200, [], "<html><head><title>My Website</title></head><body>Hi</body></html>"

    def on_POST(self, path, headers, post_data):
        if path == "/":
            return 426, [], "admin@example.com"
            # return 500, [], "Basic realm=\"test\""
        else:
            return 200, [], "<html><head><title>My Website</title></head><body>Hi</body></html>"

    def on_error(self, code, headers, message):
        return code, [("Connection", "close"), ("Content-Type", "text/html; charset=iso-8859-1")], message

    def on_complete(self, client, code, req_headers, res_headers, request, response):
        # Do something when the request is done and the response is sent
        extra = {}

        self.log(client, request, response, extra)
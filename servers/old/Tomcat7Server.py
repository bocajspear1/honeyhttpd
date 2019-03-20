from honeyhttpd.lib.server import Server

class Tomcat7Server(Server):

    def name(self):
        return "Apache Tomcat"

    def version(self):
        return "7.0.60"

    def system(self):
        return ""

    def server_version(self):
        return "Apache-Coyote/1.1"

    def responses(self):
        return {
                200: ('OK', 'Request fulfilled, document follows'), 
                201: ('Created', 'Document created, URL follows'), 
                202: ('Accepted', 'Request accepted, processing continues off-line'), 
                203: ('Non-Authoritative Information', 'Request fulfilled from cache'), 
                204: ('No Content', 'Request fulfilled, nothing follows'), 
                205: ('Reset Content', 'Clear input form for further input.'), 
                206: ('Partial Content', 'Partial content follows.'), 
                400: ('Bad Request', 'Bad request syntax or unsupported method'), 
                401: ('Unauthorized', 'No permission -- see authorization schemes'), 
                402: ('Payment Required', 'No payment -- see charging schemes'), 
                403: ('Forbidden', 'Request forbidden -- authorization will not help'), 
                404: ('Not Found', 'The requested resource ($path) is not available.'), 
                405: ('Method Not Allowed', 'Specified method is invalid for this resource.'), 
                406: ('Not Acceptable', 'URI not available in preferred format.'), 
                407: ('Proxy Authentication Required', 'You must authenticate with this proxy before proceeding.'), 
                408: ('Request Timeout', 'Request timed out; try again later.'), 
                409: ('Conflict', 'Request conflict.'), 
                410: ('Gone', 'URI no longer exists and has been permanently removed.'), 
                411: ('Length Required', 'Client must specify Content-Length.'), 
                412: ('Precondition Failed', 'Precondition in headers is false.'), 
                413: ('Request Entity Too Large', 'Entity is too large.'), 
                414: ('Request-URI Too Long', 'URI is too long.'), 
                415: ('Unsupported Media Type', 'Entity body in unsupported format.'), 
                416: ('Requested Range Not Satisfiable', 'Cannot satisfy request range.'), 
                417: ('Expectation Failed', 'Expect condition could not be satisfied.'), 
                100: ('Continue', 'Request received, please continue'), 
                101: ('Switching Protocols', 'Switching to new protocol; obey Upgrade header'), 
                300: ('Multiple Choices', 'Object has several resources -- see URI list'), 
                301: ('Moved Permanently', 'Object moved permanently -- see URI list'), 
                302: ('Found', 'Object moved temporarily -- see URI list'), 
                303: ('See Other', 'Object moved -- see Method and URL list'), 
                304: ('Not Modified', 'Document has not changed since given time'), 
                305: ('Use Proxy', 'You must use proxy specified in Location to access this resource.'), 
                307: ('Temporary Redirect', 'Object moved temporarily -- see URI list'), 
                500: ('Internal Server Error', 'Server got itself in trouble'), 
                501: ('Not Implemented', 'Server does not support this operation'), 
                502: ('Bad Gateway', 'Invalid responses from another server/proxy.'), 
                503: ('Service Unavailable', 'The server cannot process the request due to a high load'), 
                504: ('Gateway Timeout', 'The gateway server did not receive a timely response'), 
                505: ('HTTP Version Not Supported', 'Cannot fulfill request.')}

    def default_headers(self):
        return []

    def error_format(self, port):
        return """<html><head><title>""" + self.name() + "/" + self.version() + """ - Error report</title><style><!--H1 {font-family:Tahoma,Arial,sans-serif;color:white;background-color:#525D76;font-size:22px;} H2 {font-family:Tahoma,Arial,sans-serif;color:white;background-color:#525D76;font-size:16px;} H3 {font-family:Tahoma,Arial,sans-serif;color:white;background-color:#525D76;font-size:14px;} BODY {font-family:Tahoma,Arial,sans-serif;color:black;background-color:white;} B {font-family:Tahoma,Arial,sans-serif;color:white;background-color:#525D76;} P {font-family:Tahoma,Arial,sans-serif;background:white;color:black;font-size:12px;}A {color : black;}A.name {color : black;}HR {color : #525D76;}--></style> </head><body><h1>HTTP Status $code - </h1><HR size="1" noshade="noshade"><p><b>type</b> Status report</p><p><b>message</b> <u>$message</u></p><p><b>description</b> <u>$description</u></p><HR size="1" noshade="noshade"><h3>""" + self.name() + "/" + self.version() + """</h3></body></html>

"""

    def on_GET(self, path, headers):

        res_headers = [("Content-Encoding", "gzip"), ("Content-Type", "text/html;charset=UTF-8"), ("Connection", "Keep-Alive")]

        if path == "/":
            return 200, res_headers, "<html><head><title>My Website</title></head><body>Hi</body></html>"
        elif path == "/admin":
            return 403, res_headers, "<html><head><title>My Website</title></head><body>Hi</body></html>"
        else:
            return 404, [{"": "", "": ""}], ""
    
    def on_POST(self, path, headers, post_data):

        return 404, [], ""

    def on_error(self, code, headers, message):
        return code, headers, message

    # Called on any form of request. Return None, None if you wish to continue normally, or return ERROR_CODE, EXTRA
    def on_request(self, handler):
        if not handler.path.startswith("/"):
            return 400, ""
        return None, None

    def on_complete(self, client, code, req_headers, res_headers, request, response):
        # Do something when the request is done and the response is sent
        pass
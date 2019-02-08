from servers.ApacheServer import ApacheServer


import honeyhttpd.lib.encode as encode

# This server pretends to be a server with basic authentication. Collects passwords
class ApachePasswordServer(ApacheServer):
    def on_request(self, handler):
        return None, None

    def on_GET(self, path, headers):
        
        if path == "/" or path == "/index.php" or path == "/admin":
            return 401, [],  "Basic realm=\"Secure Area\""
        return 404, [], ""

    def on_POST(self, path, headers, post_data):
        return 404, [], ""

    def on_error(self, code, headers, message):
        return code, [("Connection", "close"), ("Content-Type", "text/html; charset=iso-8859-1")], message

    def on_complete(self, client, code, req_headers, res_headers, request, response):

        extra = {}

        for header in req_headers:
            # Encode the response data if the Content-Encoding is set
            if header[0].lower() == "authorization":

                auth_split = header[1].split(" ")
                if len(auth_split) > 1:
                    auth_data = auth_split[1]
                    extra['creds'] = encode.decode_base64(auth_data)

        self.log(client, request, response, extra)

    def default_headers(self):
        return [
            
        ]
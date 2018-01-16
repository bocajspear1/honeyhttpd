from servers.ApacheServer import ApacheServer


import honeyhttpd.lib.encode as encode

# This server pretends to be a server with basic authentication. Collects passwords
class ApachePasswordServer(ApacheServer):
    def on_request(self, handler):
        return None, None

    def on_GET(self, path, headers):
        if "authorization" in headers:
            auth_split = headers["authorization"].split(" ")
            if len(auth_split) > 1:
                auth_data = auth_split[1]
                print(auth_data)
                print(encode.decode_base64(auth_data))
        if path == "/" or path == "/index.php":
            return 401, [("hi", "there")],  "Basic realm=\"Secure Area\""
        return 404, [], ""

    def on_POST(self, path, headers):
        return 404, [], ""

    def on_error(self, code, headers, message):
        return code, [("Connection", "close"), ("Content-Type", "text/html; charset=iso-8859-1")], message


    def default_headers(self):
        return [
            ("wassup", "dude")
        ]
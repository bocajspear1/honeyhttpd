import datetime

class StdoutLogger(object):

    def __init__(self):
        pass

    def stores_large(self):
        return False

    def log(self, remote_ip, remote_port, is_ssl, port, request, response, extra={}):
        if len(request) > 10000:
            request = "VERY LONG REQUEST (>10000)"
        print(remote_ip, remote_port, is_ssl, port, request, response, extra)

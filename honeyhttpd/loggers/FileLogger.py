import datetime

class FileLogger(object):

    def __init__(self):
        pass

    def stores_large(self):
        return False

    def log(self, remote_ip, remote_port, is_ssl, port, request, response, extra={}):
        protocol = "http"
        if is_ssl:
            protocol = "https"
        log_path = "./logs/server-" + protocol + "-" + str(port) + ".log"
        
        output_file = open(log_path, "a")
        now = datetime.datetime.now().isoformat()
        output_file.write("\n" + now + " - From {}:{}: \n{}\nSent: \n{}\n".format(remote_ip, remote_port, request, response))
        output_file.close()

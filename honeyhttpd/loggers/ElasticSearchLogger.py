from elasticsearch import Elasticsearch
import datetime
import platform 

class ElasticSearchLogger(object):

    def __init__(self, config):
        self.__server = config['server']
        if "https:" in self.__server:
            self.__use_ssl = True
        else:
            self.__use_ssl = False

        self.__verify_certs = config['verify']

    def stores_large(self):
        return False

    def log(self, remote_ip, remote_port, is_ssl, port, request, response, extra={}):
        protocol = "http"
        if is_ssl:
            protocol = "https"
        es = Elasticsearch(self.__server, use_ssl=self.__use_ssl, verify_certs=self.__verify_certs)

        es.index(index='honeyhttpd', doc_type='connection', body={
            "time": datetime.datetime.now().isoformat(),
            "remote_ip": remote_ip,
            "remote_port": remote_port,
            "protocol": protocol,
            "port": port,
            "request": str(request),
            "response": str(response),
            "is_large": is_large,
            "host": platform.node()
        })

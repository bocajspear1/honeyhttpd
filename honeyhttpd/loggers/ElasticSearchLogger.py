from elasticsearch import Elasticsearch
import datetime
import platform 

class ElasticSearchLogger(object):

    def __init__(self, config):
        self._server = config['server']
        self._verify_certs = config['verify']
        self._username = config.get('username', '')
        self._password = config.get('password', '')
        self._api_key = config.get('api_key', '')
        self._index = config['index']

    def stores_large(self):
        return False

    def log(self, remote_ip, remote_port, is_ssl, port, request, response, extra={}):
        protocol = "http"
        if is_ssl:
            protocol = "https"
        
        es = None
        if self._username != "":
            es = Elasticsearch(self._server, basic_auth=(self._username, self._password), verify_certs=self._verify_certs )
        elif self._api_key != "":
            es = Elasticsearch(self._server, api_key=self._api_key, verify_certs=self._verify_certs )
        else:
            es = Elasticsearch(self._server, verify_certs=self._verify_certs )

        es.index(index=self._index, body={
            "time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "remote_ip": remote_ip,
            "remote_port": remote_port,
            "protocol": protocol,
            "port": port,
            "request": str(request),
            "response": str(response),
            "host": platform.node()
        })

import platform
import datetime
import boto3
import sys

if sys.version_info.major == 2:
    from urllib import urlencode
else:
    from urllib.parse import urlencode

class S3Logger(object):

    def __init__(self, config):
        self._aws_access_key_id = config['key_id']
        self._aws_secret_access_key = config['key']
        self._aws_bucket = config['bucket']

    def stores_large(self):
        return True

    def log(self, remote_ip, remote_port, is_ssl, port, request, response, extra={}):

        protocol = "http"
        if is_ssl:
            protocol = "https"

        body = str(request) + "\n\n" + str(response)

        tags = {
            "remote_ip": remote_ip,
            "remote_port": remote_port,
            "protocol": protocol,
            "port": port,
            "host" : platform.node()
        }

        s3 = boto3.resource(
            's3',
            aws_access_key_id=self._aws_access_key_id,
            aws_secret_access_key=self._aws_secret_access_key
        )

        s3.Object(self._aws_bucket, platform.node() + "/" + remote_ip + "/" + datetime.datetime.now().isoformat()).put(Body=body, Metadata=extra, Tagging=urlencode(tags))
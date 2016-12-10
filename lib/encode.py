import sys
import gzip
import zlib

def get_gzip(data):
    if sys.version_info.major == 2:
        import StringIO as io
        out = io.StringIO()
        with gzip.GzipFile(fileobj=out, mode="w") as f:
            f.write(data)
        return out.getvalue()
    else:
        data = bytes(data, 'utf-8')
        return gzip.compress(data)

def get_deflate(data):
    return zlib.compress(data)

def get_plain(data):
    if sys.version_info.major == 2:
        return data
    else:
        return data.encode('utf-8')

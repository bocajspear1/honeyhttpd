import sys
import gzip
import zlib
import base64

def encode_gzip(data):
    if sys.version_info.major == 2:
        import StringIO as io
        out = io.StringIO()
        with gzip.GzipFile(fileobj=out, mode="w") as f:
            f.write(data)
        return out.getvalue()
    else:
        data = bytes(data, 'utf-8')
        return gzip.compress(data)

def encode_deflate(data):
    return zlib.compress(data)

def encode_plain(data):
    if sys.version_info.major == 2:
        return data
    else:
        return data.encode('utf-8')

def decode_base64(data):
    decode_input = data
    if sys.version_info.major == 3:
        decode_input = decode_input.encode("utf-8")
        return base64.decodestring(decode_input).decode("utf-8")
    else:
        return base64.decodestring(decode_input)

def decode_plain(data):
    if sys.version_info.major == 2:
        return data
    else:
        return data.decode('utf-8')

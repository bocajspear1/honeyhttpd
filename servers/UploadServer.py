# Takes uploaded files and stores them
from servers.ApacheServer import ApacheServer

import time
import honeyhttpd.lib.encode as encode
import os

class UploadServer(ApacheServer):
    def on_request(self, handler):
        return None, None

    def on_GET(self, path, headers):
        print(path)   
        return 404, [], ""

    def on_POST(self, path, headers, post_data):
        if path == "/":

            file_data = None
            file_name = "upload." + str(time.time())
            sep = None

            for header in headers:
                if header[0] == "Content-Type" and 'multipart/form-data' in header[1]:
                    options = header[1].split(";")
                    for option in options:
                        if option.strip().startswith("boundary="):
                            sep = "\r\n--" + option.split("=")[1].strip()
                                
            # This just make it simpler to delimiter on seperator with \r\n
            post_data = encode.encode_plain("\r\n") + post_data

            if sep is not None:
                last_sep = sep + "--"
                # Get the last sep
                before_end = post_data.split(encode.encode_plain(last_sep))
                
                split_form = before_end[0].split(encode.encode_plain(sep))
                for chunk in split_form:
                    if encode.encode_plain("filename=") in chunk:
                        filechunks = chunk.split(encode.encode_plain("\r\n\r\n"), 1)
                        
                        # Get the name of the file uploaded
                        for metadata in filechunks[0].split(encode.encode_plain("\r\n")):
                            if encode.encode_plain("form-data") in metadata and \
                               encode.encode_plain("filename=") in metadata:
                                form_data = metadata.split(encode.encode_plain(";"))
                                for form_item in form_data:
                                    if encode.encode_plain("filename=") in form_item:

                                        formfn = form_item.split(encode.encode_plain("="), 1)[1][1:-1]
                                        # Do some basic filtering for uploaded filenames
                                        file_name += "." + encode.decode_plain(formfn).replace(".", "").replace("\\", '')
                        file_data = filechunks[1]
                        

            else:
                file_data = post_data

            if not os.path.exists(file_name):
                open("./" + file_name, "wb+").write(file_data)

            return 200, [], "OK\r\n"
        return 404, [], ""

    def on_error(self, code, headers, message):
        return code, [("Connection", "close"), ("Content-Type", "text/html; charset=iso-8859-1")], message

    def on_complete(self, client, code, req_headers, res_headers, request, response):

        extra = {}

       

        self.log(client, request, response, extra)

    def default_headers(self):
        return [
            
        ]
#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import ssl
import urlparse
import os
import subprocess
import json
import uuid

class PostHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        params = urlparse.parse_qs(urlparse.urlparse(self.path).query)

        if params.get('token') != [os.getenv('GITHUB_TOKEN')]:
            self.send_response(401)
            self.end_headers()
            return

        body = self.rfile.read(int(self.headers.getheader('content-length', 0)))
        payload = json.loads(body)

        id = str(uuid.uuid4())
        subprocess.Popen(['/ci.sh', payload['after'], id])

        self.send_response(202)
        self.end_headers()

        self.wfile.write(id)


httpd = HTTPServer(('0.0.0.0', 80), PostHandler)

if os.getenv('CERT_PATH'):
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile=os.getenv('CERT_PATH'), server_side=True)
    print('Using SSL certificate: %s' % os.getenv('CERT_PATH'))

print('Ready to CI!')
httpd.serve_forever()


#!/usr/bin/env python

import http.server
import socketserver
import ssl
import json
import uuid
from urllib.parse import parse_qs, urlparse


class Httpd:
    def __init__(self, addr, handler, logger, cert=None):
        socketserver.TCPServer.allow_reuse_address = True
        self.server = socketserver.TCPServer(addr, handler)
        self.logger = logger

        if cert:
            self.server.socket = ssl.wrap_socket(self.server.socket, certfile=cert, server_side=True)
            self.logger.info('Using SSL certificate: %s' % cert)

    def run(self):
        self.logger.info('Ready to CI!')
        self.server.serve_forever()

class PostHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server, builder, token, logger):
        self.builder = builder
        self.token = token
        self.logger = logger
        super().__init__(request, client_address, server)

    def do_POST(self):
        self.logger.debug('received HTTP POST %s' % (self.path))
        params = parse_qs(urlparse(self.path).query)

        if params.get('token') != [self.token]:
            self.logger.error('expected token "%s", got "%s"' % (self.token, params.get('token')))
            self.send_response(401)
            self.end_headers()
            return

        body = self.rfile.read(int(self.headers.get('content-length')))
        payload = json.loads(body.decode('utf-8'))

        id = str(uuid.uuid4())

        self.logger.info('Building %s for commit %s#%s' % (id, payload['repository']['full_name'], payload['after']))
        self.builder.build(payload['repository']['full_name'], payload['after'], id)

        self.send_response(202)
        self.end_headers()

        self.wfile.write(id.encode())
        self.wfile.write("\n".encode())

if __name__ == '__main__':
    from .__main__ import httpd
    httpd().run()


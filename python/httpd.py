#!/usr/bin/env python

import http.server
import socketserver
import ssl
import os
import json
import uuid
from urllib.parse import parse_qs, urlparse
from docker import Client

socket = os.environ.get('DOCKER_HOST')
cli = Client(base_url = socket)

class PostHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        params = parse_qs(urlparse(self.path).query)

        if params.get('token') != [os.getenv('GITHUB_TOKEN')]:
            self.send_response(401)
            self.end_headers()
            return

        body = self.rfile.read(int(self.headers.get('content-length')))
        payload = json.loads(body.decode('utf-8'))

        id = str(uuid.uuid4())

        socket_mount = ['%s:%s' % (x[7:], x[7:]) for x in [socket] if x.startswith('unix://')]
        container = cli.create_container(
            volumes = socket_mount,
            host_config = cli.create_host_config(binds = socket_mount),
            name = id,
            tty = True,
            environment = dict(os.environ),
            image = os.getenv('BUILD_IMAGE'),
            command = [os.getenv('BUILD_CMD'), payload['after'], id]
        )
        cli.start(container.get('Id'))

        self.send_response(202)
        self.end_headers()

        self.wfile.write(id.encode())
        self.wfile.write("\n".encode())


httpd = socketserver.TCPServer(('0.0.0.0', 80), PostHandler)

if os.getenv('CERT_PATH'):
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile=os.getenv('CERT_PATH'), server_side=True)
    print('Using SSL certificate: %s' % os.getenv('CERT_PATH'))

print('Ready to CI!')
httpd.serve_forever()


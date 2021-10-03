#!/usr/bin/env python3
# coding: utf-8
# Copyright 2021, Zhining He, Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    # citation for urlparse: https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlparse
    def get_host_port_path(self,url):
        DEFAULT_PORT = 80
        DEFAULT_PATH = "/"
        components = urllib.parse.urlparse(url)
        host = components.hostname
        port = components.port
        path = components.path
        if port is None:  # port is not given
            port = DEFAULT_PORT
        if not path:  # is an empty path
            path = DEFAULT_PATH
        return host, port, path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def get_code(self, data):
        return int(data.split()[1])

    def get_headers(self,data):
        return data.splitlines()[0]

    # get resource content
    def get_body(self, data):
        return data.split("\r\n\r\n")[-1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        host, port, path = self.get_host_port_path(url)
        # establish connection with the socket
        self.connect(host, port)

        payload = "GET %s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n" % (path, host)   
        # send request to server
        self.sendall(payload)
        
        # pharse response
        response_message = self.recvall(self.socket)
        header = self.get_headers(response_message)
        code = self.get_code(header)
        body = self.get_body(response_message)
        print(response_message)
        # close connection
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port, path = self.get_host_port_path(url)
        # establish connection with the socket
        self.connect(host, port)

        content = "" 
        if args:
            # citation for urlencode: https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlencode
            content = urllib.parse.urlencode(args)
        content_length = len(content)
        content_type = "application/x-www-form-urlencoded"
        payload = "POST %s HTTP/1.1\r\nHost: %s\r\nContent-Type: %s\r\nContent-Length: %d\r\nConnection: close\r\n\r\n" % (path, host, content_type, content_length)
        # send request to server
        self.sendall(payload + content)
        
        # pharse response
        response_message = self.recvall(self.socket)
        header = self.get_headers(response_message)
        code = self.get_code(header)
        body = self.get_body(response_message)
        print(response_message)
        # close connection
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))

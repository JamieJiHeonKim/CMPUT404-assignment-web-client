#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Ji Heon Kim
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

# Resources :       docs.python.org/3/library/http.client.html
# virtual hosting : https://stackoverflow.com/questions/27234905/programmatically-access-virtual-host-site-from-ip-python-iis

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
    #def get_host_port(self,url):

    # connecting to server using socket
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return self.socket

    # fetch code from data
    def get_code(self, data):
        code = int(self.get_headers(data)[0].split(' ')[1])
        return code

    # fetch header from data
    def get_headers(self,data):
        headers = data.split('\r\n')[:-1]
        return headers

    # fetch body from data
    def get_body(self, data):
        body = data.split('\r\n')[-1]
        return body
    
    # send all data
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

        # socket.shutdown(socket.SHUT_WR) prevents the client application from further sending the data
        # this termination is needed to prevent the server side from further attempting to read any data
        self.socket.shutdown(socket.SHUT_WR)
        
    # close socket
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

    # GET from URLs
    def GET(self, url, args=None):
        # parse url path, port, host
        urlPath = urllib.parse.urlparse(url)
        urlHost = urlPath.netloc.split(':')[0]
        request = 'GET {} HTTP/1.1\r\nHost: {}\r\n\r\n'.format('/'+urlPath.path, urlPath.netloc)

        if urlPath.port == None:
            port = 80
        else:
            port = urlPath.port

        self.connect(urlHost,port)
        self.sendall(request)
        recv = self.recvall(self.socket)

        code = self.get_code(recv)
        body = self.get_body(recv)

        self.close()
        return HTTPResponse(code, body)

    # POST to URLs
    def POST(self, url, args=None):
        # parse url path, port, host
        urlPath = urllib.parse.urlparse(url)
        urlHost = urlPath.netloc.split(':')[0]
        data = ""
        
        if urlPath.port == None:
            port = 80
        else:
            port = urlPath.port
        try:
            keys = list(args.keys())
            values = list(args.values())

            for i in range(len(keys)):
                if len(data) > 0:
                    data = data + "&"
                data = data + keys[i] + '=' + values[i]
            dataLength = len(data)
        except:
            dataLength = 0

        request = 'POST {}  HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\n'.format('/'+urlPath.path,urlPath.netloc, dataLength)

        request = request + data

        self.connect(urlHost,port)
        self.sendall(request)
        recv = self.recvall(self.socket)

        code = self.get_code(recv)
        body = self.get_body(recv)

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

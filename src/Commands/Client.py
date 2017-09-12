""" A general client program that can be adapted to be used as a client for any part of the system.
https://github.com/alexwhb/simple-python-chat-server/blob/master/server.py
https://pymotw.com/2/socket/tcp.html
http://www.binarytides.com/code-chat-application-server-client-sockets-python/

"""

import socket
import select
import sys
import os
import time
import platform
from subprocess import check_output
from multiprocessing import Process

class Client(Process):
    """ A client process that communicates with its parent through the pipe "pipe_in" and stores
        messages in "self.messages".
    """
    def __init__(self,
                 client_type,
                 pipe_in,
                 pipe_out,
                 port=5000,
                 host="localhost",
                 **kwargs):
        Process.__init__(self)
        self.client_type = client_type
        self.pipe_in = pipe_in
        self.pipe_out = pipe_out
        self.messages = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.settimeout(2)
        self.is_alive = True

        # Optional arguments
        connection_attempts=10
        self.logger=None
        self.work=None
        if "connection_attempts" in kwargs.keys():
            connection_attempts = kwargs["connection_attempts"]
        if "work" in kwargs.keys():
            self.work = kwargs["work"]
        if "logger" in kwargs.keys():
            self.logger = kwargs["logger"]
        
        
        if host == "localhost":
            host = self.get_local_ip(platform.system())

        self.host = host
        # Connect to remote host
        attempt = 0
        while attempt < connection_attempts:
            attempt += 1
            try:
                self.server.connect((host, port))
                if self.logger:
                    self.logger.log("Connected to server at ({}, {})".format(host, port))
                break
            except:
                if self.logger:
                    self.logger.log("Unable to connect to server {} at port {}. Trial {}/{}"\
                               .format(host, port, attempt, connection_attempts))
        if attempt >= connection_attempts:
            if self.logger:
                self.logger.log("Connection failed.")
            else:
                print("Connection failed.")
            os.close(self.pipe_in)
            os.close(self.pipe_out)
            self.is_alive = False
            return

        # Present the client for the server so that the server knowns what kind of client this is.
        time.sleep(1)
        self.server.send("client_type;{}".format(client_type).encode("utf-8"))

    def run(self):
        while True:
            # Windows doesn't allow non blocking select on the pipe self.pipe_in. Thus we need a workaround.
            if platform.system() == "Windows":
                socket_list = [self.server]
            else:
                socket_list = [self.pipe_in, self.server]
            # Get the list sockets which are readable
            read_sockets, _, _ = select.select(socket_list, [], [])
            for sock in read_sockets:
                #incoming message from remote server
                if sock == self.server:
                    data = sock.recv(4096)
                    if not data:
                        os.write(self.pipe_out, "disconnected".encode(encoding='utf_8'))
                    else:
                        # A small special fix for the GUI
                        if self.work:
                            self.gui_parse(data.decode("utf-8"))
                        else:
                            os.write(self.pipe_out, data)
                # Parent process entered a message
                else:
                    msg = os.read(self.pipe_in, 1024)
                    self.server.send(msg)

    def get_local_ip(self, system):
        """ The socket.gethostbyname(socket.gethostname()) - method does, apparently, not work on
            the raspberry pi. The call only returns the "localhost" address so we need some extra
            work to be able to detect the ip.
        """
        if system == "Linux":
            # This is a bit ugly but it works
            ips = check_output(['hostname', '--all-ip-addresses']).decode("utf-8")
            return ips.split(" ")[0]
        else:
            return socket.gethostbyname(socket.gethostname())

    def gui_parse(self, data):
        data = data.split(";")
        if "update" in data[0]:
            data.pop(0)
            for update in data:
                self.work.put(update)

    def close(self):
        """ Close the client.
        """
        if self.logger:
            self.logger.log("Client is terminating")
        self.server.send("close me".encode("utf-8"))
        os.close(self.pipe_in)
        os.close(self.pipe_out)
        self.server.close()

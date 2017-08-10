""" This is a ghost process that could take any form of client using manual chatting with the
    system. L
"""

import os
import sys
import select
import socket
import signal
import traceback, threading

from .Client import Client
from .Logger import Logger
class Ghost():
    BUFFER_SIZE = 1024
    def __init__(self, args):
        server_address = "localhost"
        if args["--host"]:
            server_address = args["--host"]
        client_type_ghost = args["--client_type"]

        self.logger = Logger(client_type_ghost, args)
        client_logger = Logger(client_type_ghost + " client", args)
        # Create a pipe to communicate to the client process
        self.pipe_in_client, self.pipe_out_dia = os.pipe()
        self.pipe_in_dia, self.pipe_out_client = os.pipe()
        # Create a client object to communicate with the server
        self.client = Client(client_type=client_type_ghost,
                             pipe_in=self.pipe_in_client,
                             pipe_out=self.pipe_out_client,
                             host=server_address,
                             logger=client_logger)
        self.client.start()

    def run(self):
        """ Main loop of the ghost client. It works much like a chat client.
        """
        try:
            while True:
                # Wait for either incomming message from the server (via the client) or from the user
                # via the command line
                socket_list = [sys.stdin, self.pipe_in_dia]

                # Get the list sockets which are readable
                read_sockets, _, _ = select.select(socket_list, [], [])

                for sock in read_sockets:
                    # Incoming message from remote server
                    if sock == self.pipe_in_dia:
                        data = os.read(self.pipe_in_dia, self.BUFFER_SIZE)
                        if not data:
                            raise SystemExit("Disconnected from server")
                        else:
                            self.parse(data)
                    # User entered a message
                    else:
                        msg = sys.stdin.readline()
                        os.write(self.pipe_out_dia, msg.encode("utf-8"))
                        sys.stdout.flush()
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            self.secure_close()
    
    def parse(self, data):
        data = data.decode("utf-8")
        if "disconnected" in data:
            raise SystemExit("Disconnected from server")
        else:
            self.logger.log(data)

    def secure_close(self):
        self.client.close()
        os.kill(self.client.pid, signal.SIGTERM)
        os.close(self.pipe_out_dia)
        os.close(self.pipe_in_dia)
""" This is a ghost process that could take any form of client using manual chatting with the
    system. L
"""

import os
import sys
import select
import socket

from .Client import Client

class Ghost():
    BUFFER_SIZE = 1024
    def __init__(self, client_type_ghost, server_address):
        # Create a pipe to communicate to the client process
        self.pipe_in_client, self.pipe_out_dia = os.pipe()
        self.pipe_in_dia, self.pipe_out_client = os.pipe()
        # Create a client object to communicate with the server
        self.client = Client(client_type=client_type_ghost,
                             pipe_in=self.pipe_in_client,
                             pipe_out=self.pipe_out_client,
                             host=server_address)
        self.client.start()

    def run(self):
        """ Main loop of the ghost client. It works much like a chat client.
        """
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
                        print('\nDisconnected from server')
                        sys.exit()
                    else:
                        sys.stdout.write(data.decode("utf-8") + "\n")
                        sys.stdout.flush()

                # User entered a message
                else:
                    msg = sys.stdin.readline()
                    os.write(self.pipe_out_dia, msg.encode("utf-8"))
                    sys.stdout.flush()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        SERV_ADDR = socket.gethostbyname(socket.gethostname())
        print("No server address established. Using the local address to this machine: {}"\
             .format(SERV_ADDR))
    else:
        SERV_ADDR = sys.argv[2]
    if len(sys.argv) < 2:
        print("Usage: Ghost.py <client type>")
        print("Recommended values of <client type> is 'dialouge', 'yumi', 'hololens', etc.")
    else:
        print("Starting Ghost client")
        GHOST = Ghost(sys.argv[1], SERV_ADDR)
        GHOST.run()
        print("Ghost terminated")

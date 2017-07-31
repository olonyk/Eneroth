""" This is the brain of the Dialogue experiment.
1. Receive command from user.
2. Match the command to objects in the data base.
3. Send back IDs of the objects with highest matching.
"""

import os
import sys
import select
import time
import socket

from .Client import Client
from .Guesser import Guesser

class Dialogue():
    def __init__(self, args):
        self.ambiguity_threshold = 0.9
        server_address = "localhost"
        if args["--host"]:
            server_address = args["--host"]
        if args["--ambigthresh"]:
            self.ambiguity_threshold = int(args["--ambigthresh"])
            
        # Create a pipe to communicate to the client process
        self.pipe_in_client, self.pipe_out_dia = os.pipe()
        self.pipe_in_dia, self.pipe_out_client = os.pipe()
        # Create a client object to communicate with the server
        self.client = Client(client_type="dialogue",
                             pipe_in=self.pipe_in_client,
                             pipe_out=self.pipe_out_client,
                             host=server_address)
        self.client.start()

        # Create a guesser object that ranks the options and estimates ambiguity.
        self.guesser = Guesser(args["data_file"], guess_type="tfidf")

        self.state = "initial"

    def run(self):
        """ Main loop of the dialouge client. It works much like a chat client.
        """
        while True:
            # Wait for either incomming message from the server (via the client) or from the user
            # via the command line
            socket_list = [self.pipe_in_dia]

            # Get the list sockets which are readable
            read_sockets, _, _ = select.select(socket_list, [], [])

            for sock in read_sockets:
                # Incoming message from remote server
                if sock == self.pipe_in_dia:
                    data = os.read(self.pipe_in_dia, 32).decode("utf-8")
                    if not data:
                        print('\nDisconnected from server')
                        sys.exit()
                    else:
                        #print data
                        self.interpret(data)

    def interpret(self, data):
        """ Interprets the messages from the Hololens and takes the appropriate action.
        """
        if self.state == "initial":
            # If this is the first iteration, we need to ask the guesser to rank the options.
            self.guesser.new_guess(data)
            # Get the most likely object
            (guess_id, guess_x, guess_y, certainty) = self.guesser.get_top_guess()
            self.state = "iterating"
        else:
            # This check needs to be better!
            if "no" in data:
                # Remove the object that the guesser semed likely and get the next guess.
                self.guesser.remove_top_guess()
                (guess_id, guess_x, guess_y, certainty) = self.guesser.get_top_guess()
            else:
                # Get the next (or the first) guess from the guesser.
                (guess_id, guess_x, guess_y, _) = self.guesser.get_top_guess()
                certainty = 1
                self.state = "initial"

        if certainty < self.ambiguity_threshold:
            # If we have to high ambiguity we guess by point at the object
            os.write(self.pipe_out_dia, "yumi;point at ({},{})".format(guess_x, guess_y)\
                     .encode("utf-8"))
            time.sleep(0.5)
            # And ask the Hololens if we made the right decision
            os.write(self.pipe_out_dia, "hololens;Did you mean the object with id: {}?"\
                     .format(guess_id).encode("utf-8"))
        else:
            # If there is little ambiguity we give the user the object
            os.write(self.pipe_out_dia, "yumi;retrieve object at ({},{})"\
                     .format(guess_x, guess_y).encode("utf-8"))
            self.state = "initial"
        self.guesser.print_guess_order()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        SERV_ADDR = socket.gethostbyname(socket.gethostname())
        print("No server address established. Using the local address to this machine: {}"\
             .format(SERV_ADDR))
    else:
        SERV_ADDR = sys.argv[2]
    if len(sys.argv) < 2:
        DATA = "default_data.csv"
        print("No datafile was selected. Using default data: {}".format(DATA))
    else:
        DATA = sys.argv[1]
    print("Starting Dialouge client")
    DIA = Dialogue(DATA, SERV_ADDR)
    DIA.run()
    print("Dialouge client terminated")

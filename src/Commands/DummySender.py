

import sys
import os
import random
import time
import signal
import traceback, threading
from .Client import Client
from .Logger import Logger

class Dummy:
    def __init__(self, args):
        server_address = "localhost"
        num_stuff = 10
        self.delay = 1
        if args["--host"]:
            server_address = args["--host"]
        if args["--nrobj"]:
            num_stuff = int(args["--nrobj"])
        if args["--delay"]:
            self.delay = float(args["--delay"])

        self.logger = Logger("DummySender", args)
        client_logger = Logger("DummySender client", args)

        # Create a pipe to communicate to the client process
        self.pipe_in_client, self.pipe_out_dia = os.pipe()
        self.pipe_in_dia, self.pipe_out_client = os.pipe()
        # Create a client object to communicate with the server
        self.client = Client(client_type="DummyClient",
                             pipe_in=self.pipe_in_client,
                             pipe_out=self.pipe_out_client,
                             host=server_address,
                             logger=client_logger)
        self.client.start()
        X = random.sample(range(50), num_stuff)
        Y = random.sample(range(50), num_stuff)
        self.objects = [[id, x/100, y/100] for (id, (x, y)) in enumerate(list(zip(X, Y)))]


    def run(self):
        while self.objects:
            msg = ";".join(["{},{},{}".format(unit[0], unit[1], unit[2]) for unit in self.objects])
            self.logger.log("Sending " + msg)
            os.write(self.pipe_out_dia, "hololens;{}".format(msg)\
                     .encode("utf-8"))
            time.sleep(self.delay)
            self.random_remove()
            self.random_move()
        self.client.close()
        
        os.kill(self.client.pid, signal.SIGTERM)
        os.close(self.pipe_out_dia)
        os.close(self.pipe_in_dia)

    def random_remove(self):
        self.objects.pop(random.randint(0, len(self.objects)-1))

    def random_move(self):
        rng = [1, 2]
        for an_object in self.objects:
            for i in rng:
                an_object[i] += random.randint(-10, 10)/100
                an_object[i] = float("{0:.2f}".format(an_object[i]))
                if an_object[i] < 0:
                    an_object[i] = 0
                elif an_object[i] > 0.5:
                    an_object[i] = 0.5

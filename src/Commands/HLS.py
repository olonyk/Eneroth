""" This is the Hololens experiment Server that connects the hololens with all the other parts of
    the system.
"""

import socket
import select
import traceback
import platform
from subprocess import check_output
from .Logger import Logger
import re

class Server:
    """ A simple TCP server.
    """
    def __init__(self, args):
        self.logger = Logger("Server", args)

        # List to keep track of socket descriptors
        self.connection_dict = {}
        self.new_connections = []
        self.recv_buffer = 4096 # Advisable to keep it as an exponent of 2
        self.port = 5000

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # In order to get the correct (local) ip we need to detect which platform we are running on
        server_address = self.get_local_ip(platform.system())
        server_address = (server_address, self.port)
        self.server_socket.bind(server_address)
        self.server_socket.listen(10)

        # Add server socket to the list of readable connections
        self.connection_dict["server"] = self.server_socket
        self.logger.log("Server started\t addr:\t{}\tport:{} ".format(self.server_socket.getsockname()[0],\
                                                               self.server_socket.getsockname()[1]))
        # Create a backlog of undelivered messages
        self.backlog = []

        # Create a list of sockets to ignore
        self.ignore = []

    def run(self):
        """ The main loop of the server.
        """
        while True:
            # Get the list sockets which are ready to be read through select
            all_connections = list(self.connection_dict.values()) + self.new_connections
            read_sockets, _, _ = select.select(all_connections, [], [])

            for sock in read_sockets:
                # Check if we should ignore this connection
                try:
                    if sock.getpeername() in self.ignore:
                        continue
                except:
                    pass
                finally:
                    pass
                #New connection
                if sock == self.server_socket:
                    # Handle the case in which there is a new connection recieved through
                    # server_socket
                    sockfd, addr = self.server_socket.accept()
                    self.new_connections.append(sockfd)
                    self.logger.log("Client (%s, %s) connected" % addr)

                #Some incoming message from a client
                else:
                    # Data recieved from client, process it
                    try:
                        #In Windows, sometimes when a TCP program closes abruptly,
                        # a "Connection reset by peer" exception will be thrown
                        data = sock.recv(self.recv_buffer)
                        self.logger.log("Recieved: '{}' from addr: {}".format(data.decode("utf-8"),\
                                                                         sock.getpeername()))
                        if data:
                            self.parse(sock, data)
                    except:
                        self.logger.log("Client (%s, %s) is offline" % addr)
                        traceback.print_exc()
                        sock.close()
                        self.remove_socket(sock)
                        continue

        self.server_socket.close()

    def remove_socket(self, socket_rem):
        """ Remove a socket from the dictionary of sockets if they appear to be broken.
        """
        clients_to_pop = []
        # Iterate through the dictionary to find the client to pop. Can't pop the clien during the
        # iteration because the dictionary size will change and you will get the error:
        # RuntimeError: dictionary changed size during iteration
        # Instead save the clients to pop in the clients_to_pop list.
        for client, sock in self.connection_dict.items():
            if sock == socket_rem:
                clients_to_pop.append(client)

        # Now iterate through the clients_to_pop list and remove the clients from the dictionary.
        if len(clients_to_pop) > 0:
            for client in clients_to_pop:
                self.connection_dict.pop(client, None)
                self.logger.log("Client: {} ".format(client) + "has been removed from the connection" \
                         + "list, due to a broken socket.")

    def parse(self, sock, data):
        """ Split the data at figure out whether this is a new client presenting itself or a
            message that should be sent to a specific clien.
        """
        data = data.decode("utf-8")
        tmp = ""
        # Clean up if the client sent faulty chars
        for char in data:
            if not ord(char) < 32 or ord(char) > 126:
                tmp += char
        data = tmp
        # Try to figure out if the message is from a browser, if so close it
        if "User-Agent:" in data:
            print("The socket {} is ignored.".format(sock.getpeername()))
            self.ignore.append(sock.getpeername())
            return
        data = data.split(";")
        if data[0] == "close me":
            self.remove_socket(sock)

        elif data[0] == "client_type":
            self.logger.log("A new client, '{}', has joined with addr {}".format(data[1], \
                     sock.getpeername()))
            # New client
            for new_socket in self.new_connections:
                if new_socket == sock:
                    self.connection_dict[data[1]] = new_socket
                    self.new_connections.remove(new_socket)
                    self.send_from_backlog()
                    return
            self.logger.log("Warning! The new client: {} was not found in".format(data[1]) \
                     + " the list of connections")
        else:
            # A message that should be forwarded
            recipient_found = False
            for client, recipient_socket in self.connection_dict.items():
                if client == data[0]:
                    recipient_found = True
                    self.send(recipient_socket, ";".join(data[1:]))
            if not recipient_found:
                if not sock:
                    return
                self.logger.log("Message added to backlog")
                self.backlog.append(";".join(data).encode("utf-8"))
            else:
                return 1

    def send(self, recipient_socket, message):
        """ The send command handles the forwarding of messages to different clients of the system.
        """
        try:
            recipient_socket.send(message.encode('utf-8'))
            for client, sock in self.connection_dict.items():
                if sock == recipient_socket:
                    self.logger.log("A message '{}' has been sent to client '{}'".format(message, client))
        except:
            # Broken socket connection may be, chat client pressed ctrl+c for example
            recipient_socket.close()
            self.remove_socket(recipient_socket)

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

    def send_from_backlog(self):
        """ Try to resend the messages in backlog.
        """
        delete_backlog_posts = []
        for msg in self.backlog:
            delete_backlog_posts.append(self.parse(False, msg))
        for i, delete in reversed(list(enumerate(delete_backlog_posts))):
            print("{}: {}".format(delete, delete==True))
            if delete:
                self.backlog.pop(i)
        #self.logger.log("Backlog: {}".format(", ".join(self.backlog)))


import os

from tkinter import Tk, BOTH
from tkinter.ttk import Frame, Label, Button
from tkinter import StringVar, IntVar
from tkinter import *
import tkinter as ttk

from .Client import Client


class ReachTester(Frame):
    def __init__(self, args):
        self.root = Tk()
        
        Frame.__init__(self, self.root)
        
        self.grid()
        self.master.title("Reach tester")
        self.client_tuple = self.connect()

        self.valid_values = (0, 0.05 ,0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95)
        lbl_x = Label(self.master, text="X:")
        lbl_y = Label(self.master, text="Y:")
        btn_p = Button(self.master, text="Pick", command=self.pick)
        self.sb_x = ttk.Spinbox(self.master, values=self.valid_values)
        self.sb_y = ttk.Spinbox(self.master, values=self.valid_values)
        
        lbl_x.grid(row=0, column=0, sticky=E+N)
        self.sb_x.grid(row=0, column=1, sticky=E+N)
        lbl_y.grid(row=1, column=0, sticky=E+N)
        self.sb_y.grid(row=1, column=1, sticky=E+N)
        btn_p.grid(row=2, column=1, sticky=E+N)
        
    def connect(self):
        # Create a pipe to communicate to the client process
        pipe_in_client, pipe_out_dia = os.pipe()
        pipe_in_dia, pipe_out_client = os.pipe()
        # Create a client object to communicate with the server
        client = Client(client_type="GUI client",
                        pipe_in=pipe_in_client,
                        pipe_out=pipe_out_client)

        if client.is_alive:
            client.start()
            return (client, pipe_in_client, pipe_out_dia, pipe_in_dia, pipe_out_client)
        return None

    def pick(self):
        msg = "yumi;pick;{};{}".format(self.sb_x.get(), self.sb_y.get())
        self.client_tuple[0].server.send(msg.encode("utf-8"))
    
    def run(self):
        self.root.mainloop()
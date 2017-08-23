
from os import listdir
from os.path import isfile, join, splitext, isdir

from tkinter import Tk, BOTH
from tkinter.ttk import Frame, Radiobutton, Label, Scrollbar, Button, OptionMenu, Entry
from tkinter import StringVar, IntVar
from tkinter import *
import tkinter as ttk


class GUI_setup(Frame):
    def __init__(self, kernel, master=None):
        Frame.__init__(self, master)
        self.kernel = kernel
        
        self.grid()
        self.master.title("YuMi experiment")
        self.client_tuple = None
        self.master.protocol("WM_DELETE_WINDOW", self.kernel.on_closing)
        #self.master.geometry("100x100+500+100")

        config = self.kernel.read_config()
        

        frame_session_type = Frame(self.master, relief=GROOVE, borderwidth=2)
        frame_participant = Frame(self.master, relief=GROOVE, borderwidth=2)
        frame_data_bases = Frame(self.master, relief=GROOVE, borderwidth=2)
        frame_server = Frame(self.master, relief=GROOVE, borderwidth=2)
        
        # Session type
        self.rbType = StringVar(self.master)
        
        lbl1 = Label(frame_session_type, text="Session type")
        rb1 = Radiobutton(frame_session_type, text="Hololens", variable=self.rbType, value="hololens", command=self.type)
        rb2 = Radiobutton(frame_session_type, text="Monitor", variable=self.rbType, value="monitor", command=self.type)
        rb3 = Radiobutton(frame_session_type, text="Dialogue", variable=self.rbType, value="dialogue", command=self.type)
        
        self.rbType.set("hololens")
        rb1.select()
        rb2.deselect()
        rb3.deselect()

        lbl1.grid(row=0, column=0, sticky=W+N)
        rb1.grid(row=1, column=0, sticky=W+N)
        rb2.grid(row=2, column=0, sticky=W+N)
        rb3.grid(row=3, column=0, sticky=W+N)

        # Data base
        self.data_base_path = config["data_base_path"]
        try:
            listdir(self.data_base_path)
        except FileNotFoundError:
            self.data_base_path = "/"
        
        data_files = [f for f in listdir(self.data_base_path) if isfile(join(self.data_base_path, f))]
        data_files = [files for files in data_files if ".csv" in files]
        self.data_file = StringVar(master)
        if len(data_files) == 0:
            data_files.append("No data found")
        self.data_file.set(data_files[0])

        lbl2 = Label(frame_data_bases, text="Data base")
        btn_browse = Button(frame_data_bases, text="Browse", command=self.kernel.browse_db)
        self.db_drop = OptionMenu(frame_data_bases, self.data_file, *data_files)
        
        self.data_base_file = join(self.data_base_path, self.data_file.get())

        lbl_db1 = Label(frame_data_bases, text="Found in:")
        lbl_db2 = Label(frame_data_bases, text="Choose:")

        lbl_text = self.data_base_path
        if len(lbl_text) > 30:
            lbl_text = "..." + lbl_text[-30:]
        self.lbl_db3 = Label(frame_data_bases, text=lbl_text)

        lbl2.grid(row=0, column=0, columnspan=1, sticky=W+N)
        lbl_db2.grid(row=1, column=0, columnspan=1, sticky=W+N)
        self.db_drop.grid(row=1, column=1, columnspan=3, sticky=E+N)
        lbl_db1.grid(row=2, column=0, columnspan=1, sticky=W+N)
        self.lbl_db3.grid(row=2, column=1, columnspan=3, sticky=W+N)
        btn_browse.grid(row=3, column=3, sticky=E+N)

        # Participant
        self.write_to_path = config["write_to_path"]
        try:
            listdir(self.write_to_path)
        except FileNotFoundError:
            self.write_to_path = "/"
        part_dirs = [f for f in listdir(self.write_to_path) if isdir(join(self.write_to_path, f))]
        part_dirs = [dirs for dirs in part_dirs if "participant" in dirs]
        parts = [" ".join(part.split("_")[0:2]) for part in part_dirs]
        self.participant = StringVar()
        self.participant.set("New participant") # default value
        parts = [self.participant.get()] + parts



        lbl_part = Label(frame_participant, text="Name:")
        self.part_entry = Entry(frame_participant, textvariable=self.participant)

        lbl3 = Label(frame_participant, text="Participant")
        
        lbl_text = self.write_to_path
        if len(lbl_text) > 10:
            lbl_text = "..." + lbl_text[-10:]
        self.lbl4 = Label(frame_participant, text=lbl_text)
        lbl5 = Label(frame_participant, text="Save to:")
        self.dropdown_participant = OptionMenu(frame_participant, self.participant, *parts)
        btn_browse2 = Button(frame_participant, text="Browse", command=self.kernel.browse_part)

        lbl_part.grid(row=1, column=0, sticky=W+N)
        self.part_entry.grid(row=1, column=1, sticky=W+N)
        lbl3.grid(row=0, column=0, sticky=W+N)
        self.dropdown_participant.grid(row=2, column=1, columnspan=2, sticky=W+N+E)
        
        lbl5.grid(row=3, column=0, columnspan=1, sticky=W+N)
        self.lbl4.grid(row=3, column=1, sticky=W+N)
        btn_browse2.grid(row=4, column=1, sticky=E+N)

        

        # Server
        self.addr = StringVar(master)
        self.addrs = config["server_adrs"].split(";")
        self.addr.set(self.addrs[0])

        self.port = StringVar(master)
        self.ports = config["server_ports"].split(";")
        self.port.set(self.ports[0])

        lbl6 = Label(frame_server, text="Connect to server")
        lbl7 = Label(frame_server, text="Server address:")
        lbl8 = Label(frame_server, text="Server port:")

        self.rbServer1 = StringVar(self.master)
        
        rb4 = Radiobutton(frame_server, text="", variable=self.rbServer1, value="entry", command=self.server1)
        rb5 = Radiobutton(frame_server, text="", variable=self.rbServer1, value="list", command=self.server1)
        self.rbServer1.set("entry")
        rb4.select()
        rb5.deselect()
        self.adr_entry = Entry(frame_server, textvariable=self.addr)
        self.adr_drop = OptionMenu(frame_server, self.addr, *self.addrs)
        self.adr_drop['state'] = 'disabled'

        self.rbServer2 = StringVar(self.master)

        rb6 = Radiobutton(frame_server, text="", variable=self.rbServer2, value="entry", command=self.server2)
        rb7 = Radiobutton(frame_server, text="", variable=self.rbServer2, value="list", command=self.server2)
        rb6.select()
        rb7.deselect()
        self.rbServer2.set("entry")
        self.port_entry = Entry(frame_server, textvariable=self.port)
        self.port_drop = OptionMenu(frame_server, self.port, *self.ports)
        self.port_drop['state'] = 'disabled'

        lbl8 = Label(frame_server, text="Status:")
        lbl_text = "Not connected"
        if self.kernel.client_tuple:
            lbl_text = "Connected to {}".format(self.kernel.client_tuple[0].host)
        self.lbl9 = Label(frame_server, text=lbl_text)
        btn_connect = Button(frame_server, text="Connect", command=self.kernel.connect)

        lbl6.grid(row=0, column=0, sticky=W+E+N+S)
        lbl7.grid(row=1, column=0, rowspan=2, sticky=W)
        rb4.grid(row=1, column=2, columnspan=1, rowspan=1, sticky=W)
        self.adr_entry.grid(row=1, column=3, columnspan=1, rowspan=1, sticky=W+E+N+S)
        rb5.grid(row=2, column=2, columnspan=1, rowspan=1, sticky=W)
        self.adr_drop.grid(row=2, column=3, columnspan=1, rowspan=1, sticky=W+E+N+S)

        lbl8.grid(row=3, column=0, rowspan=2, sticky=W)
        rb6.grid(row=3, column=2, columnspan=1, rowspan=1, sticky=W)
        self.port_entry.grid(row=3, column=3, columnspan=1, rowspan=1, sticky=W+E+N+S)
        rb7.grid(row=4, column=2, columnspan=1, rowspan=1, sticky=W)
        self.port_drop.grid(row=4, column=3, columnspan=1, rowspan=1, sticky=W+E+N+S)

        lbl8.grid(row=5, column=0, columnspan=1, rowspan=1, sticky=W)
        self.lbl9.grid(row=5, column=3, columnspan=1, rowspan=1, sticky=W)
        btn_connect.grid(row=6, column=3, columnspan=1, rowspan=1, sticky=W)


        # Layout
        btn_launch = Button(self.master, text="Launch", command=self.kernel.launch)
        frame_session_type.grid(row=0,column=0, columnspan=1, rowspan=1, sticky=W+E+N+S)
        frame_data_bases.grid(row=1, column=1, columnspan=1, rowspan=1, sticky=W+E+N+S)
        frame_participant.grid(row=1, column=0, columnspan=1, rowspan=1, sticky=W+E+N+S)
        frame_server.grid(row=0, column=1, columnspan=1, rowspan=1, sticky=W+E+N+S)
        btn_launch.grid(row=2, column=1, sticky=E)

    def type(self):
        pass
        
    def server1(self):
        if self.rbServer1.get() == "entry":
            self.adr_entry['state'] = 'normal'
            self.adr_drop['state'] = 'disabled'
        else:
            self.adr_entry['state'] = 'disabled'
            self.adr_drop['state'] = 'normal'
    
    def server2(self):
        if self.rbServer2.get() == "entry":
            self.port_entry['state'] = 'normal'
            self.port_drop['state'] = 'disabled'
        else:
            self.port_entry['state'] = 'disabled'
            self.port_drop['state'] = 'normal'
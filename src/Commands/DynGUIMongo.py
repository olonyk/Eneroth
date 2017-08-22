
import os.path
from os import listdir
from os.path import isfile, join, splitext, isdir
from PIL import Image, ImageTk
import PIL
from io import BytesIO
from tkinter import Tk, BOTH
from tkinter.ttk import Frame, Radiobutton, Label, Scrollbar, Button
from tkinter import StringVar
from tkinter import *
import tkinter as ttk
from tkinter.filedialog import askdirectory
from pkg_resources import resource_string, resource_listdir, resource_filename
import sys
import csv

from pymongo import MongoClient
from .Client import Client
from .Logger import Logger
from .BuildDB import BuildDB
from .GUI_setup import GUI_setup

class GUI_kernel:
    def __init__(self, args):

        self.client_tuple = None
        self.root_setup = None
        self.app = None

        self.root_setup = Tk()
        self.app_setup = GUI_setup(self, master=self.root_setup)
        self.root_setup.mainloop()

        # Set up logger and verboser to handle log and verbose
        self.logger = Logger("GUI_kernel", args)
        if args["--data_file"]:
            builder = BuildDB(args)
            self.mongo_db = builder.build()
            self.logger.log("A new data base with size {} created."\
                            .format(len(list(self.mongo_db.find()))))
        else:
            self.mongo_client = MongoClient(args["--host"], args["--port"])

        

        #root = Tk()
        #self.app = GUI(self, master=root)
        #root.mainloop()

        """
        a_post = self.mongo_db.find_one()
        image_byte = a_post["<img>"]

        stream = BytesIO(image_byte)
        img = Image.open(stream)
        img.show()"""

    def run(self):
        pass
    
    def get_colors(self):
        return [color.lower() for color in list(self.mongo_db.distinct("#Color"))]

    def get_shapes(self):
        return [shape.lower() for shape in list(self.mongo_db.distinct("#Shape"))]

    def update_filter(self, gui):
        if len(gui.view_labels) > 0:
            [label.grid_forget() for label in gui.view_labels]
            gui.view_labels = []
        if gui.color.get() == "all" and gui.shape.get() == "all":
            filtered_items = list(self.mongo_db.find({}, {"<img>": 1, "_id": 0,
                                                          "ID":1, "X":1, "Y":1}))
        elif gui.color.get() == "all":
            filtered_items = list(self.mongo_db.find({"#Shape": gui.shape.get()},
                                                     {"<img>": 1, "_id": 0,
                                                      "ID":1, "X":1, "Y":1}))
        elif gui.shape.get() == "all":
            filtered_items = list(self.mongo_db.find({"#Color": gui.color.get()},
                                                     {"<img>": 1, "_id": 0,
                                                      "ID":1, "X":1, "Y":1}))
        else:
            filtered_items = list(self.mongo_db.find({"#Color": gui.color.get(),
                                                      "#Shape": gui.shape.get()},
                                                     {"<img>": 1, "_id": 0,
                                                      "ID":1, "X":1, "Y":1}))
        gui.photos = []
        if len(filtered_items) > 0:
            # Calculate how many images to display per row.
            image = PIL.Image.open(BytesIO(filtered_items[0]["<img>"]))
            items_per_row = int(gui.view_canvas.winfo_width() / image.size[0])

            for i, item in enumerate(filtered_items):
                photo = ImageTk.PhotoImage(PIL.Image.open(BytesIO(item["<img>"])))
                lbl = Label(gui.view_frame, image=photo)
                gui.view_labels.append(lbl)
                gui.photos.append(photo)
            self.layout(None)
            self.send(filtered_items)

    def layout(self, event):
        if len(self.app.view_labels) > 0:
            items_per_row = int(self.app.view_canvas.winfo_width() / self.app.view_labels[0].winfo_width())
            if items_per_row < 1:
                items_per_row = 1
            for i, widget in enumerate(self.app.view_labels):
                widget.grid(row=int(i/items_per_row), column=i%items_per_row)

    def new_experiment(self):
        print("new_experiment")

    def connect(self):
        args = {"-l":True, "-v":True}
        client_logger = Logger("GUI client", args)

        # Add adrs and port to configure and to the drop downs
        self.app_setup.addrs.append(self.app_setup.addr.get())
        self.app_setup.ports.append(self.app_setup.port.get())
        self.app_setup.addrs = list(set(self.app_setup.addrs))
        self.app_setup.ports = list(set(self.app_setup.ports))

        self.app_setup.adr_drop['menu'].delete(0, 'end')
        for choice in self.app_setup.addrs:
            self.app_setup.adr_drop['menu'].add_command(label=choice,
                                                        command=ttk._setit(self.app_setup.addr,
                                                                           choice))
        self.app_setup.port_drop['menu'].delete(0, 'end')
        for choice in self.app_setup.addrs:
            self.app_setup.port_drop['menu'].add_command(label=choice,
                                                         command=ttk._setit(self.app_setup.port,
                                                                            choice))

        # Create a pipe to communicate to the client process
        pipe_in_client, pipe_out_dia = os.pipe()
        pipe_in_dia, pipe_out_client = os.pipe()
        # Create a client object to communicate with the server
        client = Client(client_type="GUI client",
                        port=int(self.app_setup.port.get()),
                        host=self.app_setup.addr.get(),
                        pipe_in=pipe_in_client,
                        pipe_out=pipe_out_client,
                        logger=client_logger)
        
        if client.is_alive:
            client.start()
            self.client_tuple = (client, pipe_in_client, pipe_out_dia, pipe_in_dia, pipe_out_client)
            self.app_setup.lbl9['text'] = "Connected to {}".format(client.host)
        else:
            self.app_setup.lbl9['text'] = "Connection failed"


    def send(self, filtered_items):
        if self.client_tuple:
            msg = []
            for item in filtered_items:
                msg.append("{},{},{}".format(item["ID"],
                                             item["X"],
                                             item["Y"]))
            msg = ";".join(msg)
            os.write(self.client_tuple[2], "hololens;{}".format(msg).encode("utf-8"))
    
    def on_closing(self):
        if self.client_tuple:
            self.client_tuple[0].close()
        if self.app:
            self.app.destroy()
        if self.app_setup:
            config = {"data_base_path":self.app_setup.data_base_path,
                      "write_to_path":self.app_setup.write_to_path,
                      "server_adrs":";".join(self.app_setup.addrs),
                      "server_ports":";".join(self.app_setup.ports)}
            with open(resource_filename("Commands.resources.config", "config.dat"), 'w') as f:
                writer = csv.writer(f, delimiter=':')
                for key, value in config.items():
                    writer.writerow([key, value])            
        if self.root_setup:
            self.root_setup.destroy()
        sys.exit(0)
    
    def read_config(self):
        with open(resource_filename("Commands.resources.config", "config.dat")) as f:
            config = f.readlines()
        config = [con.strip().split(":") for con in config]
        return {key : value for key, value in config}

    def browse_db(self):
        data_base_path = askdirectory(initialdir = self.app_setup.data_base_path, title="Select folder with data bases")
        if data_base_path:
            data_files = [f for f in listdir(data_base_path) if isfile(join(data_base_path, f))]
            data_files = [files for files in data_files if ".csv" in files]
            if len(data_files) == 0:
                data_files.append("No data found")
            self.app_setup.data_file.set(data_files[0])
            self.app_setup.db_drop['menu'].delete(0, 'end')
            for choice in data_files:
                self.app_setup.db_drop['menu'].add_command(label=choice,
                                                           command=ttk._setit(self.app_setup.data_file,
                                                                              choice))
            self.app_setup.data_base_path = data_base_path
            if len(data_base_path) > 10:
                data_base_path = "..." + data_base_path[-10:]
            self.app_setup.lbl_db3["text"] = data_base_path
    
    def browse_part(self):
        participant_path = askdirectory(initialdir = self.app_setup.write_to_path, title="Select folder")
        if participant_path:
            self.app_setup.write_to_path = participant_path
            part_dirs = [f for f in listdir(participant_path) if isdir(join(participant_path, f))]
            part_dirs = [dirs for dirs in part_dirs if "participant" in dirs]
            print(part_dirs)
            parts = [" ".join(part.split("_")[0:2]) for part in part_dirs]
            parts = ["New participant"] + parts
            self.app_setup.dropdown_participant['menu'].delete(0, 'end')
            for part in parts:
                self.app_setup.dropdown_participant['menu'].add_command(label=part,
                                                           command=ttk._setit(self.app_setup.participant,
                                                                              part))
            lbl_text = participant_path
            if len(lbl_text) > 10:
                lbl_text = "..." + lbl_text[-10:]
            self.app_setup.lbl4["text"] = lbl_text
    
    def launch(self):
        
            


class GUI(Frame):
    def __init__(self, kernel, master=None):
        Frame.__init__(self, master)
        self.kernel = kernel
        
        self.grid()
        self.master.title("YuMi experiment")
        self.master.geometry("950x950+500+100")

        # Create option frame where the buttons are located and the view frame where the images
        # are shown
        #self.master.rowconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.bind('<Configure>', self.kernel.layout)
        self.master.protocol("WM_DELETE_WINDOW", self.kernel.on_closing)
        self.option_frame = Frame(master, bg="white")
        self.option_frame.grid(row=0, column=0, sticky=W+E+N+S)
        self.view_canvas = ttk.Canvas(master, borderwidth=0, background="white")

        self.view_frame = Frame(self.view_canvas, background="white")
        self.vsb = Scrollbar(master, orient="vertical", command=self.view_canvas.yview)
        self.view_canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.grid(row=1, column=0, sticky=E+N+S)
        self.view_canvas.grid(row=1, column=0, sticky=W+E+N+S)
        self.view_canvas.create_window((4,4), window=self.view_frame, anchor="nw", 
                                       tags="self.frame")

        self.view_frame.bind("<Configure>", self.onFrameConfigure)

        # This list is used to keep a reference of the images displayed in the view frame.
        self.photos = []

        # This list is to be able to reference the labels and delete them when the filter 
        # is updated.
        self.view_labels = []

        btn_frame = Frame(self.option_frame, bg="white")
        btn_frame.grid(row=0, column=2, rowspan=1, padx=(30, 30), sticky=W+E+N+S)
        btn = Button(btn_frame, text="Start", command=self.kernel.new_experiment)
        btn.grid(row=0, column=10, padx=(30, 30), sticky=N+W+E)
        btn = Button(btn_frame, text="Pick", command=self.kernel.new_experiment)
        btn.grid(row=2, column=10, padx=(30, 30), sticky=N+W+E)
        btn = Button(btn_frame, text="Restart", command=self.kernel.new_experiment)
        btn.grid(row=3, column=10, padx=(30, 30), sticky=N+W+E)

        #btn = Button(self.option_frame, text="Connect to server", command=self.kernel.connect)
        #btn.grid(row=1, column=10, padx=(30, 30), sticky=N+W)

        # Set up the option frame. Start with the color radiobuttons
        self.color_frame = Frame(self.option_frame, background="white")
        self.color_frame.grid(row=0, column=0, rowspan=2, padx=(30, 30), sticky=W+E+N+S)
        lbl = Label(self.color_frame, text="Color filter", background="white")
        lbl.grid(row=0, column=0, columnspan=5)

        self.color = StringVar()
        self.color.set("all")
        colors = self.kernel.get_colors()
        image = PIL.Image.open(resource_filename("Commands.resources.images",
                                                 "default_dont_know.png"))
        photo_def = ImageTk.PhotoImage(image)
        image_select = PIL.Image.open(resource_filename("Commands.resources.images",
                                                        "default_dont_know_sel.png"))
        photo_select_def = ImageTk.PhotoImage(image_select)
        rb1 = Radiobutton(self.color_frame, image=photo_def, selectimage=photo_select_def,
                          variable=self.color, value="all", command=lambda:self.kernel.update_filter(self),
                          indicatoron=False)
        rb1.grid(row=1, column=0, rowspan=2, sticky=W+E+N+S)

        # Use this list to keep references to the images used in the buttons. Without a reference
        # the garbage collector will remove them!
        self.images = []
        self.images.append(photo_select_def)
        self.images.append(photo_def)
        for i, col in enumerate(colors):
            image = PIL.Image.open(resource_filename("Commands.resources.images",
                                                     "{}.png".format(col)))
            photo = ImageTk.PhotoImage(image)
            image_select = PIL.Image.open(resource_filename("Commands.resources.images",
                                                            "{}_sel.png".format(col)))
            photo_select = ImageTk.PhotoImage(image_select)
            rb = Radiobutton(self.color_frame, image=photo, selectimage=photo_select,
                             variable=self.color, value=col, command=lambda:self.kernel.update_filter(self),
                             indicatoron=False)
            rb.grid(row=(int((i+1)/5)*2)+1, column=(i+1)%5, rowspan=2, sticky=W+E+N+S)
            rb.deselect()
            self.images.append(photo_select)
            self.images.append(photo)
        
        self.shape_frame = Frame(self.option_frame, background="white")
        self.shape_frame.grid(row=0, column=1, rowspan=2, padx=(30, 30), sticky=W+E+N+S)
        lbl = Label(self.shape_frame, text="Shape filter", background="white")
        lbl.grid(row=0, column=0, columnspan=5)

        self.shape = StringVar()
        self.shape.set("all")
        shapes = self.kernel.get_shapes()
        rb1 = Radiobutton(self.shape_frame, image=photo_def, selectimage=photo_select_def,
                          variable=self.shape, value="all", command=lambda:self.kernel.update_filter(self),
                          indicatoron=False)
        rb1.grid(row=1, column=0, rowspan=2, sticky=W+E+N+S)

        for i, sha in enumerate(shapes):
            image = PIL.Image.open(resource_filename("Commands.resources.images",
                                                     "shape_{}.png".format(sha)))
            photo = ImageTk.PhotoImage(image)
            image_select = PIL.Image.open(resource_filename("Commands.resources.images",
                                                            "shape_{}_sel.png".format(sha)))
            photo_select = ImageTk.PhotoImage(image_select)
            rb = Radiobutton(self.shape_frame, image=photo, selectimage=photo_select,
                             variable=self.shape, value=sha, command=lambda:self.kernel.update_filter(self),
                             indicatoron=False)
            rb.grid(row=(int((i+1)/5)*2)+1, column=(i+1)%5, rowspan=2, sticky=W+E+N+S)
            rb.deselect()
            self.images.append(photo_select)
            self.images.append(photo)
        
        #self.kernel.update_filter(self)
        

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.view_canvas.configure(scrollregion=self.view_canvas.bbox("all"))

class Connect_GUI(Frame):
    def __init__(self, kernel, master=None):
        Frame.__init__(self, master)
        self.kernel = kernel
        self.grid()
        self.master.title("YuMi experiment")

        btn = Button(master, text="Connect to localhoast", command=self.connect_localhoast)
        btn.grid(row=0, column=0, padx=(30, 30), sticky=N+W)
    
    def connect_localhoast(self):
        args = {"-l":True, "-v":True}
        client_logger = Logger("GUI client", args)

        # Create a pipe to communicate to the client process
        pipe_in_client, pipe_out_dia = os.pipe()
        pipe_in_dia, pipe_out_client = os.pipe()
        # Create a client object to communicate with the server
        client = Client(client_type="GUI client",
                        pipe_in=pipe_in_client,
                        pipe_out=pipe_out_client,
                        logger=client_logger)
        client.start()

        self.kernel.client_tuple = (client, pipe_in_client, pipe_out_dia, pipe_in_dia, pipe_out_client)
        self.master.destroy()
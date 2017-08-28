
import csv
import os.path
import sys
from datetime import datetime
from io import BytesIO
from os import listdir
from os.path import exists, isdir, isfile, join, splitext
from tkinter import Tk, BOTH, Toplevel, StringVar, IntVar, S, N, E, W, _setit, messagebox
from tkinter.ttk import Frame, Radiobutton, Label, Scrollbar, Button, OptionMenu, Entry, Checkbutton
from tkinter.filedialog import askdirectory

import PIL
from PIL import Image, ImageTk
from pkg_resources import resource_filename, resource_listdir, resource_string

from pymongo import MongoClient

from .BuildDB import BuildDB
from .Client import Client
from .GUI_filter import GUI_filter
from .GUI_setup import GUI_setup
from .Logger import Logger


class GUI_kernel:
    def __init__(self, args):

        self.client_tuple = None
        self.root_setup = None
        self.app = None
        self.run_time = False
        self.log_file = False
        self.filtered_items = []

        self.root_setup = Tk()
        self.app_setup = GUI_setup(self, master=self.root_setup)
        self.root_setup.mainloop()

    def run(self):
        pass
# Methods associated with GUI_setup
    def read_config(self):
        config = {}
        with open(resource_filename("Commands.resources.config", "config.dat"), 'r') as f:
            csv_reader = csv.reader(f, delimiter=":")
            for row in csv_reader:
                if len(row) > 0:
                    config[row[0]] = row[1]

        return config

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
                                                           command=_setit(self.app_setup.data_file,
                                                                              choice))
            self.app_setup.data_base_path = data_base_path
            self.app_setup.data_base_file = join(data_base_path, self.app_setup.data_file.get())
            if len(data_base_path) > 30:
                data_base_path = "..." + data_base_path[-30:]
            self.app_setup.lbl_db3["text"] = data_base_path
    
    def browse_part(self):
        participant_path = askdirectory(initialdir = self.app_setup.write_to_path, title="Select folder")
        if participant_path:
            self.app_setup.write_to_path = participant_path
            part_dirs = [f for f in listdir(participant_path) if isdir(join(participant_path, f))]
            part_dirs = [dirs for dirs in part_dirs if "participant" in dirs]
            parts = [" ".join(part.split("_")[0:2]) for part in part_dirs]
            parts = ["New participant"] + parts
            self.app_setup.dropdown_participant['menu'].delete(0, 'end')
            for part in parts:
                self.app_setup.dropdown_participant['menu'].add_command(label=part,
                                                           command=_setit(self.app_setup.participant,
                                                                              part))
            lbl_text = participant_path
            if len(lbl_text) > 10:
                lbl_text = "..." + lbl_text[-10:]
            self.app_setup.lbl4["text"] = lbl_text
    
    def connect(self):
        args = {"-l":False, "-v":False}
        client_logger = Logger("GUI client", args)

        # Add adrs and port to configure and to the drop downs
        self.app_setup.addrs.append(self.app_setup.addr.get())
        self.app_setup.ports.append(self.app_setup.port.get())
        self.app_setup.addrs = list(set(self.app_setup.addrs))
        self.app_setup.ports = list(set(self.app_setup.ports))

        self.app_setup.adr_drop['menu'].delete(0, 'end')
        for choice in self.app_setup.addrs:
            self.app_setup.adr_drop['menu'].add_command(label=choice,
                                                        command=_setit(self.app_setup.addr,
                                                                           choice))
        self.app_setup.port_drop['menu'].delete(0, 'end')
        for choice in self.app_setup.addrs:
            self.app_setup.port_drop['menu'].add_command(label=choice,
                                                         command=_setit(self.app_setup.port,
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

    def launch(self):
        if self.app_setup:
            # Check if a database file is chosen
            if not isfile(self.app_setup.data_base_file):
                messagebox.showinfo("Error", "The file {} is not found"\
                                    .format(self.app_setup.data_base_file))
                return

            # Check if the system is connected to a server
            if not self.client_tuple:
                if not messagebox.askyesno("No connection to server", "Continue anyway?"):
                    return
            
            # Create a new participant folder
            folder_name = "participant_{}_session_{}".format(self.app_setup.participant.get(),
                                                             self.app_setup.rbType.get())
            folder_name_tmp = folder_name
            nmbr = 1
            while True:
                if exists(join(self.app_setup.write_to_path, folder_name_tmp)):
                    folder_name_tmp = "{}_{}".format(folder_name, nmbr)
                    nmbr += 1
                else:
                    os.makedirs(join(self.app_setup.write_to_path, folder_name_tmp))
                    break
            
            self.log_file = join(self.app_setup.write_to_path, folder_name_tmp)
            self.log_file = join(self.log_file, "log.csv")

            # Read and create data base
            builder = BuildDB({"--data_file":self.app_setup.data_base_file})
            self.mongo_db = builder.build()

            self.log("info","Session started")
            self.log("info","Participant: {}".format(self.app_setup.participant.get()))
            self.log("info","Experiment: {}".format(self.app_setup.rbType.get()))
            self.log("info","Data base: {}".format(self.app_setup.data_base_file))
            self.log("info","Data size: {}".format(len(list(self.mongo_db.find()))))
            if not self.client_tuple:
                self.log("info","Server adr: {}".format("None"))
            else:
                self.log("info","Server adr: {}".format(self.client_tuple[0].host))
            self.log("","")

            root = Toplevel()
            self.app = GUI_filter(self,
                                  master=root,
                                  title="{} {}".format(self.app_setup.participant.get(),
                                                       self.app_setup.rbType.get()),
                                  session_type=self.app_setup.rbType.get())
            self.app.launch()
            root.mainloop()

# Methods associated with GUI_filter
    def get_colors(self):
        return [color.lower() for color in list(self.mongo_db.distinct("#Color"))]

    def get_shapes(self):
        return [shape.lower() for shape in list(self.mongo_db.distinct("#Shape"))]

    def update_filter(self, gui):
        if len(gui.view_labels) > 0:
            [label.grid_forget() for label in gui.view_labels]
            [chekb.grid_forget() for chekb in gui.view_checks]
            gui.view_labels = []
            gui.view_checks = []
            gui.view_ch_val = []
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
            image = PIL.Image.open(BytesIO(filtered_items[0]["<img>"]))
            items_per_row = int(gui.view_canvas.winfo_width() / image.size[0])

            for i, item in enumerate(filtered_items):
                photo = ImageTk.PhotoImage(PIL.Image.open(BytesIO(item["<img>"])))
                val = IntVar()
                val.set(1)
                gui.view_checks.append(Checkbutton(gui.view_frame, image=photo, variable=val, command=self.send_pos))
                gui.view_labels.append(Label(gui.view_frame, text=item["ID"], background="white"))
                gui.view_ch_val.append(val)
                gui.photos.append(photo)
            self.layout(None)
            self.filtered_items = filtered_items
            self.send_pos()
        
        self.log("new filter", "Color: {} Shape: {}".format(gui.color.get(), gui.shape.get()))

    def layout(self, event):
        if len(self.app.view_labels) > 0:
            # Calculate how many images to display per row.
            items_per_row = int(self.app.view_canvas.winfo_width() / self.app.view_checks[0].winfo_width())
            if items_per_row < 1:
                items_per_row = 1
            for i, widget in enumerate(self.app.view_labels):
                self.app.view_checks[i].grid(row=int(i/items_per_row), column=i%items_per_row)
                widget.grid(row=int(i/items_per_row), column=i%items_per_row, sticky=S+E, padx=(0, 5), pady=(0, 5))

    def new_experiment(self):
        print("new_experiment")

    def send_pos(self):
        """ Send id and position to the reciever depending on the experiment type
        """
        if self.client_tuple:
            msg = []
            for i, item in enumerate(self.filtered_items):
                if self.app.view_ch_val[i].get():
                    msg.append("{},{},{}".format(item["ID"],
                                                item["X"],
                                                item["Y"]))
            msg = ";".join(msg)
            msg = "{};{}".format(self.app.session_type, msg)
            self.log("send", msg)
            os.write(self.client_tuple[2], msg.encode("utf-8"))
    
    def send_pick(self, block):
        """ Send a "pick" command to the YuMi robot
        """
        if self.client_tuple:
            msg = "yumi;pick;{};{}".format(block[1], block[2])
            os.write(self.client_tuple[2], msg.encode("utf-8"))

    def on_closing(self):
        if self.client_tuple:
            self.client_tuple[0].close()
        if self.app:
            self.log("info", "session exit")
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

    def start(self):
        # (Re)set the runtime
        self.run_time = datetime.now()
        # (Re)set the filter options
        self.app.color.set("all")
        self.app.shape.set("all")
        self.update_filter(self.app)
        self.log("start", "Start")
    
    def pick(self):
        if len(self.filtered_items) > 0:
            block = False
            for i, item in enumerate(self.filtered_items):
                if self.app.view_ch_val[i].get():
                    block = (item["ID"], item["X"], item["Y"])
                    break
            if block:
                self.log("pick", "Pick block {d[0]} at ({d[1]}, {d[2]})".format(d=block))
                self.send_pick(block)
                self.run_time = datetime.now()
        


    def log(self, msg_type, msg):
        time = datetime.now()
        curr_time = ""
        if self.run_time:
            curr_time = time - self.run_time
        msg = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}\t{}\t{}\t{}".format(time.year,
                                                                         time.month,
                                                                         time.day,
                                                                         time.hour,
                                                                         time.minute,
                                                                         time.second,
                                                                         curr_time,
                                                                         msg_type,
                                                                         msg)
        if self.log_file:
            with open(self.log_file, "a") as log_file:
                log_file.write(msg + "\n")

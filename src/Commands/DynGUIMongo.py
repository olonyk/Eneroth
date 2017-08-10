

from PIL import Image
from io import BytesIO
from tkinter import Tk, BOTH
from tkinter.ttk import Frame, Radiobutton
from tkinter import *

from pymongo import MongoClient
from .Logger import Logger
from .BuildDB import BuildDB

class GUI_kernel:
    def __init__(self, args):
        # Set up logger and verboser to handle log and verbose
        self.logger = Logger("GUI_kernel", args)
        if args["--data_file"]:
            builder = BuildDB(args)
            self.mongo_db = builder.build()
            self.logger.log("A new data base with size {} created."\
                            .format(len(list(self.mongo_db.find()))))
        else:
            self.mongo_client = MongoClient(args["--host"], args["--port"])



        root = Tk()
        app = GUI(self, master=root)
        root.mainloop()

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

    def color_selected(self):
        print("color selected")

class GUI(Frame):
    def __init__(self, kernel, master=None):
        Frame.__init__(self, master)
        self.kernel = kernel
        
        self.grid()
        self.master.title("Grid Manager")
        self.master.geometry("950x950+500+100")

        # Create option frame where the buttons are located and the view frame where the images
        # are shown
        self.master.rowconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)   
        self.master.columnconfigure(0, weight=1)

        self.option_frame = Frame(master, bg="red")
        self.option_frame.grid(row = 0, column = 0, sticky = W+E+N+S)
        self.view_frame = Frame(master, bg="blue")
        self.view_frame.grid(row = 1, column = 0, sticky = W+E+N+S)

        # Set up the option frame. Start with the color radiobuttons
        color = 0
        colors = self.kernel.get_colors()
        for i, col in enumerate(colors):
            rb = Radiobutton(self.option_frame, text="\n{}\n".format(col.upper()), bg=col, variable=color, value=1,
                             command=self.kernel.color_selected)
            rb.grid(row=int(i/5)*2, column=i%5, rowspan=2, sticky=W+E+N+S)
        print(colors)
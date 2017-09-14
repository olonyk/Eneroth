import csv
import os.path
import sys
from io import BytesIO
from os import listdir
from tkinter import Tk, BOTH
from tkinter.ttk import Frame, Radiobutton, Label, Scrollbar, Button, OptionMenu, Entry
from tkinter import StringVar, IntVar
from tkinter import *
import tkinter as ttk

import PIL
from PIL import Image, ImageTk
from pkg_resources import resource_filename, resource_listdir, resource_string

from pymongo import MongoClient

from .BuildDB import BuildDB
from .Client import Client
from .GUI_setup import GUI_setup
from .Logger import Logger


class GUI_filter(Frame):
    def __init__(self, kernel, master=None, title="", session_type="N/A"):
        self.title = title
        self.session_type = session_type
        Frame.__init__(self, master)
        self.kernel = kernel
    
    def launch(self):
        self.grid()
        self.master.title(self.title)
        self.master.geometry("950x950+500+100")

        # Use this list to keep references to the images used in the buttons. Without a reference
        # the garbage collector will remove them!
        self.images = []

        # Create option frame where the buttons are located and the view frame where the images
        # are shown
        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.bind('<Configure>', self.kernel.layout)
        self.master.protocol("WM_DELETE_WINDOW", self.kernel.close_filter)
        self.option_frame = Frame(self.master, bg="white")
        self.option_frame.grid(row=0, column=0, sticky=W+E+N+S)
        self.view_canvas = ttk.Canvas(self.master, borderwidth=0, background="white")

        self.view_frame = Frame(self.view_canvas, background="white")
        self.vsb = Scrollbar(self.master, orient="vertical", command=self.view_canvas.yview)
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
        self.view_checks = []
        self.view_ch_val = []

        btn_frame = Frame(self.option_frame, bg="white")
        btn_frame.grid(row=0, column=2, rowspan=1, padx=(30, 30), sticky=W+E+N+S)

        btn = Button(btn_frame, text="Pick", command=self.kernel.send_pick)
        btn.grid(row=0, column=0, padx=(5, 5), sticky=N+W+E)
        btn = Button(btn_frame, text="Point", command=self.kernel.send_point)
        btn.grid(row=1, column=0, padx=(5, 5), sticky=N+W+E)
        btn = Button(btn_frame, text="No", command=self.kernel.log_no)
        btn.grid(row=2, column=0, padx=(5, 5), sticky=N+W+E)
        self.start_btn = Button(btn_frame, text="Start", command=self.kernel.start)
        self.start_btn.grid(row=0, column=1, padx=(5, 5), sticky=N+W+E)
        btn = Button(btn_frame, text="End session", command=self.kernel.close_filter)
        btn.grid(row=1, column=1, padx=(5, 5), sticky=N+W+E)
        btn = Button(btn_frame, text="Unselect all", command=self.kernel.unselect)
        btn.grid(row=2, column=1, padx=(5, 5), sticky=N+W+E)
        btn = Button(btn_frame, text="Remove", command=self.kernel.find_and_remove)
        btn.grid(row=3, column=1, padx=(5, 5), sticky=N+W+E)

        img1 = ImageTk.PhotoImage(PIL.Image.open(resource_filename("Commands.resources.images",
                                                                   "back.png")))
        self.init_lbl = Label(btn_frame, image=img1, bg="white")
        self.init_lbl.grid(row=0, column=2, padx=(5, 5), sticky=N+W+E)
        self.images.append(img1)

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
        
        self.kernel.update_filter(self)
        

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.view_canvas.configure(scrollregion=self.view_canvas.bbox("all"))

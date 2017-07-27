
import sys
from tkinter import *
from tkinter import ttk
from tkinter import font

from Guesser import Guesser

class DynGUI:
    def __init__(self, data):
        data_handler = Guesser(data, guess_type="structured")
        self.data_handler = data_handler
        # Set up the GUI
        self.top = Tk()
        self.top.wm_title("Attribute chooser")

        # Get all attribute labels
        attributes = data_handler.get_attributes()
        self.attributes_frame = Frame(self.top, relief=GROOVE)
        self.attributes_frame.grid(row=0, column=0, columnspan=len(attributes))
        Label(self.attributes_frame, text="Attrubutes").grid(row=0, column=0)

        self.option_menu_dic = {}
        for i, attr in enumerate(attributes):
            # Create a label with the attribute name
            Label(self.attributes_frame, text=attr).grid(row=1, column=i)

            # Get the values associated with the attribute
            values = data_handler.get_attribute_values(attr)
            values = tuple(["All"] + values)

            # Create a an option menu (dropdown list) with the possible values
            var = StringVar()
            var.set(values[0])
            opt_m = OptionMenu(self.attributes_frame, var, *values,
                               command=self.option_menu_changed)
            opt_m.grid(row=2, column=i)
            self.option_menu_dic[attr] = var

        # Create the list, which is a Treeview-widget
        self.object_frame = Frame(self.top, relief=RAISED)
        self.object_frame.grid(row=1, column=0, columnspan=len(attributes), sticky='nsew')

        self.image_size = 50, 50
        tree_columns, tree_data = data_handler.get_object_data(im_size=self.image_size)
        style = ttk.Style(self.top)
        style.configure('Calendar.Treeview', rowheight=self.image_size[0])

        self.tree = ttk.Treeview(self.object_frame, columns=tree_columns, style='Calendar.Treeview')
        vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew',
                       in_=self.object_frame, columnspan=len(attributes))
        vsb.grid(column=len(attributes), row=0, sticky='ns', in_=self.object_frame)
        hsb.grid(column=0, row=1, sticky='ew', in_=self.object_frame)

        # Keep a list of all images so that they are all referenced to avoid the garbage collector
        # to remove them.
        self.images = []
        self.build_tree(tree_data, tree_columns)


        # Show the GUI by letting the root window enter the main loop
        self.top.mainloop()

    def build_tree(self, tree_data, tree_columns):
        """ Fill the tree with data and images.
        """
        self.images = []
        for col in tree_columns:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=font.Font().measure(col.title()))

        for item in tree_data:
            if item["image"]:
                # Add the current image to the list of images so the garbage collector doesn't
                # remove it.
                self.images.append(item["image"])

                self.tree.insert("", 'end', values=item["data"], image=item["image"], open=True)
            else:
                self.tree.insert("", 'end', values=item["data"])

            # adjust columns lenghts if necessary
            for indx, val in enumerate(item["data"]):
                ilen = font.Font().measure(val) + 10
                if self.tree.column(tree_columns[indx], width=None) < ilen:
                    self.tree.column(tree_columns[indx], width=ilen)

    def option_menu_changed(self, _):
        """ We enter this method when the user changes the value of the option menu. I.e. when a
            new filter is set.
        """
        qualifiers = {}
        for key in self.option_menu_dic.keys():
            qualifiers[key] = self.option_menu_dic[key].get()

        self.tree.delete(*self.tree.get_children())
        tree_columns, tree_data = self.data_handler.get_object_data(im_size=self.image_size,
                                                                    qualifiers=qualifiers)
        self.build_tree(tree_data, tree_columns)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        DATA = "default_data.csv"
        print("No datafile was selected. Using default data: {}".format(DATA))
    else:
        DATA = sys.argv[1]
    print("Starting Dynamic GUI")
    GUI = DynGUI(DATA)
    #GUI.run()
    print("Dynamic GUI terminated")

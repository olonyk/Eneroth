""" The Guesser class takes and imput message and tries to figure out which object in the data
    base was referenced. It needs a data file to be initialized and can currently handle two types
    of guesses: random guess (default) and TF/IDF.
"""

import csv
import os
import math
from tkinter import *
from random import shuffle
from PIL import ImageTk, Image
from textblob import TextBlob as tb

class Guesser:
    """ See docstring above.
    """
    MARKER_ID = "ID"
    MARKER_X = "X"
    MARKER_Y = "Y"
    MARKER_ATTRIBUTE = "#"
    MARKER_IMG = "<img>"

    def __init__(self, data_file, guess_type="random"):
        # Read the data file
        self.data_file_path = os.path.dirname(os.path.realpath(data_file))
        with open(data_file, 'r') as tmp_file:
            reader = csv.reader(tmp_file, delimiter=';')
            data_base = list(reader)

        self.guess_type = guess_type
        self.guess_order = []

    # Format the data into a nested dictionary in the following format:
    # (id-value): 'position':   (X, Y)              (coordinates as a tuple)
    #             'id':         id-value            (an integer value)
    #             'keywords':   tb(attributes)      (a textblob object with the attributes)
    #             'attributes': (attribute):    'attribute-value' (a dictionary with the attributes)
        self.objects_data = {}
        for i, object_row in enumerate(data_base):
            # From the first line (the headder) the column description is read.
            if i == 0:
                index_id = object_row.index(self.MARKER_ID)
                index_x = object_row.index(self.MARKER_X)
                index_y = object_row.index(self.MARKER_Y)
                try:
                    index_img = object_row.index(self.MARKER_IMG)
                except:
                    index_img = None
                data_indecies = [object_row.index(s) for s in object_row \
                                 if s.startswith(self.MARKER_ATTRIBUTE)]
                # Remove the MARKER_ATTRIBUTE from the headding
                data_base[0] = [s.replace("#", "") for s in object_row]
            else:
                tmp_data = {}
                tmp_data["keywords"] = tb(" ".join(object_row[i] for i in data_indecies))
                tmp_data["attributes"] = {data_base[0][i]: object_row[i] for i in data_indecies}
                tmp_data["position"] = (object_row[index_x], object_row[index_y])
                tmp_data["id"] = object_row[index_id]
                if index_img:
                    tmp_data[self.MARKER_IMG] = object_row[index_img]
                self.objects_data[object_row[index_id]] = tmp_data

    def new_guess(self, input):
        """ Create a new guess order.
        """
        if self.guess_type == "tfidf":
            self.create_guess_order_tfidf(input)
        else:
            self.create_guess_order_rand()

    def get_top_guess(self):
        """ Return the top guess from the guess order.
        """
        guess_id, certainty = self.guess_order[0]
        guess_x, guess_y = self.objects_data[guess_id]["position"]
        return (guess_id, guess_x, guess_y, certainty)

    def remove_top_guess(self):
        """ Remove the top guess from the guess order and recalculate the certainty levels.
        """
        self.guess_order.pop(0)
        certainty_tot = sum(obj[1] for obj in self.guess_order)
        self.guess_order = [[id, certainty/certainty_tot] for [id, certainty] in self.guess_order]

    def create_guess_order_rand(self):
        """ Create a random guess order with ambiguity/certainty 1/N where N is the number of items
            in the data base.
        """
        ids = self.objects_data.keys()
        certainty = 1/len(ids)
        self.guess_order = [[id, certainty] for id in ids]
        shuffle(self.guess_order)

    def create_guess_order_tfidf(self, input):
        """ Create a guess order according to term frequency divided by inverse document
            frequeency. Where the documents are defined as the keywords associated with the
            objects in the data base.
        """
        doc_list = [self.objects_data[id]["keywords"] for id in self.objects_data.keys()]
        scores = []
        score_tot = 0
        for object_id in self.objects_data.keys():
            doc = self.objects_data[object_id]["keywords"]
            score = sum(self.tfidf(word, doc, doc_list) for word in input.split(" "))
            score += 0.1 # Add small number for smothing
            score_tot += score
            scores.append([object_id, score])

        self.guess_order = [[object_id, score/score_tot] for object_id, score in scores]
        self.guess_order.sort(key=lambda x: x[1], reverse=True)


    def tf(self, word, blob):
        """ Calculate the term frequency.
        """
        return blob.words.count(word) / len(blob.words)

    def n_containing(self, word, doc_list):
        """ Calculate the number of times 'word' occurs in the corpus.
        """
        return sum(1 for doc in doc_list if word in doc.words)

    def idf(self, word, doc_list):
        """ Calculate the inverse document frequency.
        """
        return math.log(len(doc_list) / (1 + self.n_containing(word, doc_list)))

    def tfidf(self, word, doc, doc_list):
        """ Calculate the term frequency / inverse document frequency for 'word'.
        """
        return self.tf(word, doc) * self.idf(word, doc_list)

    def print_guess_order(self):
        print("ID\tCertainty")
        for id, certainty in self.guess_order:
            print("{:4}-\t{:.2f}".format(id, certainty))
        
    def get_attributes(self):
        """ Return the attribute names as a list
        """
        for _, an_object in self.objects_data.items():
            return list(an_object["attributes"].keys())

    def get_attribute_values(self, attribute):
        """ Return all values associated to an attribute.
        """
        values = []
        for _, an_object in self.objects_data.items():
            values.append(an_object["attributes"][attribute])
        return list(set(values))

    def get_object_data(self, qualifiers=None, im_size = (50, 50)):
        """ Return all the objects in a list(tuple())-structure.
            Each tuple should have (relevance, id, [image], ...)
        """
        do_columns = True
        columns = []
        data = []
        rel_pts_max = 0
        for obj_id, an_object in self.objects_data.items():
            obj_tuple = []
            if qualifiers:
                # Handle relevance.
                rel_pts = 0
                for key, value in qualifiers.items():
                    if an_object["attributes"][key] == value:
                        rel_pts += 1
                if rel_pts > rel_pts_max:
                    rel_pts_max = rel_pts
                obj_tuple.append(rel_pts)
            else:
                # If there are no qualifiers then we set relevance to zero for all objects.
                obj_tuple.append(0)

            obj_tuple.append(obj_id)

            if do_columns:
                columns = ["Relevance", "ID"]

            try:
                image_file = an_object[self.MARKER_IMG]
                image_file = os.path.join(self.data_file_path, image_file)
                image = Image.open(image_file)
                image.thumbnail(im_size, Image.ANTIALIAS)
                image = ImageTk.PhotoImage(image)
            except:
                image = None

            attrbutes = list(an_object["attributes"].keys())
            attrbutes.sort()
            for attr in attrbutes:
                obj_tuple.append(an_object["attributes"][attr])
                if do_columns:
                    columns.append(attr)
            if do_columns:
                do_columns = False
            data.append({"data":obj_tuple, "image":image})

        if qualifiers:
            for obj in data:
                obj["data"][0] = int((obj["data"][0]/rel_pts_max * 100)) / 100.0
            data = sorted(data, key=lambda k: k["data"][0], reverse=True)
        return tuple(columns), data
            
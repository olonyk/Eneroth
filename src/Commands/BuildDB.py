
import csv
from os.path import dirname
from os.path import join
import re

from pymongo import MongoClient
from bson.binary import Binary

from .Logger import Logger

class BuildDB:
    def __init__(self, args):
        # Set up logger and verboser to handle log and verbose
        self.data_file = args["--data_file"]
        self.data_dir = dirname(args["--data_file"])

    
    def build(self):
        # Read the given CSV file
        with open(self.data_file, newline='') as csvfile:
            raw_data = list(csv.reader(csvfile, delimiter=";"))

        # Pop the header to use as a reference for the fields in the data base
        header = raw_data.pop(0)

        # Create the database to fill with data
        client = MongoClient()
        db = client.database

        # Iterate through the raw data and insert it to the MongoDB
        posts = []
        img_idx = header.index("<img>")
        nam_idx = header.index("#Name")
        col_idx = header.index("#Color")
        header.append("#Shape")
        for data_row in raw_data:
            # Format the image
            image_file = open(join(self.data_dir, data_row[img_idx]), 'rb').read()
            data_row[img_idx] = Binary(image_file)

            # Color to lower case
            data_row[col_idx] = data_row[col_idx].lower()

            # Add a shape tag
            data_row.append(self.get_shape(data_row[nam_idx]))

            # Add the entry to post
            posts.append({tag : data for tag, data in zip(header, data_row)})

        # Remove all posts in db
        db.objects.remove({})

        # Insert new documents
        db.objects.insert_many(posts)
        return db.objects

    def get_shape(self, name):
        regex = r"^Brick \d+[X]\d+"
        if "Roof Tile" in name:
            return "slope"
        elif re.match( regex, name, re.M|re.I):
            return "regular"
        return "round"
        
""" A simple log object for the other objects in Eneroth to use.
"""
from datetime import datetime

class Logger():
    """ A simple log object for the other objects in Eneroth to use.
    """
    def __init__(self, name, args):
        self.do_log = False
        self.do_print = False
        self.name = name

        # Set log behaviour
        if args["-l"]:
            self.do_log = True
            self.log_file = "log_txt.txt"
        if args["-v"]:
            self.do_print = True
    
    def log(self, message):
        """ Add a time stamp and write the message to the log file.
        """
        if self.do_log or self.do_print:
            time = datetime.now()
            time_stamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}\t{}\t".format(time.year, time.month,\
                                                                            time.day, time.hour, \
                                                                            time.minute, time.second,\
                                                                            self.name)
            message = "{}\t{}".format(time_stamp, message)
            if self.do_print:
                print(message)
            if self.do_log:
                with open(self.log_file, "a") as log_file:
                    log_file.write(message + "\n")
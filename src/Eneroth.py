"""Usage:
    Eneroth.py Server [-vlth]
    Eneroth.py Dialogue [-th] (--data_file=DB) [--host=HOST] [--ambigthresh=AMBIGTHRESH]
    Eneroth.py DummySender [-vth] [--host=HOST] [--nrobj=NROBJ] [--delay=DELAY]
    Eneroth.py Ghost [-vth] (--client_type=CLIENT_TYPE) [--host=HOST] 
    Eneroth.py GUI [-vtl] [--data_file=DB]

Options:
  -h          help
  -v          verbose mode
  -t          time execution
  -l          log

Values:
  host        Address to server. Default value is "localhost".
  data_file   A csv data file with parts. To be extended other types of data bases.
  nrobj       Number of random object to generate. Default value is 10.
  delay       Sleep time between update from DummySender. Default value is 1.0.
  client_type Which client type to take.

Example:
  python3.5 Eneroth.py Server -vlt
  python3.5 Eneroth.py Dialogue -th --data_file=db.csv --host=192.168.0.100 --ambigthresh=0.5
  python3.5 Eneroth.py DummySender -vth --host=192.168.0.100 --nrobj=20 --delay=2.0
  python3.5 Eneroth.py Ghost -vth --client_type=hololens --host=192.168.0.100
  python3.5 Eneroth.py GUI -vt --data_file=lego/Lego_DB.csv
  
If you are trying to start a local mongo process and get the following error:
    Failed to start mongodb.service: Unit mongodb.service not found.
Run:
    sudo systemctl enable mongod
    sudo service mongod restart
"""

from docopt import docopt
from datetime import datetime

from Commands.DummySender import Dummy
from Commands.HLS import Server
from Commands.Dialogue import Dialogue
from Commands.Ghost import Ghost
from Commands.DynGUIMongo import GUI_kernel

if __name__ == '__main__':
    args = docopt(__doc__)
    #print(args)
    COMMAND = None
    if args["-h"]:
        print(__doc__)
    elif args["DummySender"]:
        COMMAND = Dummy(args)
    elif args["Server"]:
        COMMAND = Server(args)
    elif args["Dialogue"]:
        COMMAND = Dialogue(args)
    elif args["Ghost"]:
        COMMAND = Ghost(args)
    elif args["GUI"]:
        COMMAND = GUI_kernel(args)
    if COMMAND:
        if args["-t"]:
            S_TIME = datetime.now()
        COMMAND.run()
        if args["-t"]:
            print("Execution time:\t{}".format(datetime.now() - S_TIME))
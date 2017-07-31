"""Usage:
    Eneroth.py Server [-vlth]
    Eneroth.py Dialogue [-th] (--data_file=DB) [--host=HOST] [--ambigthresh=AMBIGTHRESH]
    Eneroth.py DummySender [-vth] [--host=HOST] [--nrobj=NROBJ] [--delay=DELAY]

Options:
  -h       help
  -v       verbose mode
  -t       time execution
  -l       log
"""

from docopt import docopt
from datetime import datetime
from Commands.DummySender import Dummy
from Commands.HLS import Server
from Commands.Dialogue import Dialogue

if __name__ == '__main__':
  args = docopt(__doc__)
  print(args)
  command = None
  if args["-h"]:
    print(__doc__)
  elif args["DummySender"]:
    command = Dummy(args)
  elif args["Server"]:
    command = Server(args)
  elif args["Dialogue"]:
    command = Dialogue(args)
  if command:
    if args["-t"]:
      startTime = datetime.now()
    command.run()
    if args["-t"]:
      print("Execution time:\t{}".format(datetime.now() - startTime))
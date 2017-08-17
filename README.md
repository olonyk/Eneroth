# Eneroth  
### Usage:
```sh
Eneroth.py Server [-vlth]
Eneroth.py Dialogue [-th] (--data_file=DB) [--host=HOST] [--ambigthresh=AMBIGTHRESH]
Eneroth.py DummySender [-vth] [--host=HOST] [--nrobj=NROBJ] [--delay=DELAY]
Eneroth.py Ghost [-vth] (--client_type=CLIENT_TYPE) [--host=HOST] 
Eneroth.py GUI [-vtl] [--data_file=DB]
```

| Options  |   |
| ------ | ------ |
| -h | help |
| -v | verbose mode |
| -t | time execution |
| -l | log |

|  Arguments |   |
| ------ | ------ |
| host |  Address to server. Default value is "localhost". |
| data_file | A csv data file with parts. To be extended other types of data bases. |
| nrobj | Number of random object to generate. Default value is 10. |
| delay | Sleep time between update from DummySender. Default value is 1.0. |
| client_type | Which client type to take. |

### Example:
```sh
  python3.5 Eneroth.py Server -vlt
  python3.5 Eneroth.py Dialogue -th --data_file=db.csv --host=192.168.0.100 --ambigthresh=0.5
  python3.5 Eneroth.py DummySender -vth --host=192.168.0.100 --nrobj=20 --delay=2.0
  python3.5 Eneroth.py Ghost -vth --client_type=hololens --host=192.168.0.100
  python3.5 Eneroth.py GUI -vt --data_file=lego/Lego_DB.csv
 ```
 
 ### User example:
 1. Start a server in a terminal:
 ```sh
$ python3.5 Eneroth.py Server -vlt
```
2. Either start a *ghost hololens* by:
 ```sh
$ python3.5 Eneroth.py Ghost -v --client_type=hololens
```
in a new shell, or by connecting a real hololens to the server started above.
3. Start the GUI by:
 ```sh
$ python3.5 Eneroth.py GUI -vt --data_file=path/to/file/Lego_DB.csv
```
4. In the GUI click on "Connect to server" and click "Connect to localhoast" in the new window (see TODO list below).
5. Use the color and shape filters to filter lego parts. Note that the lego parts will show up after a (any) filter is selected.

### Todos
 - Add a **Dependencies** section to this document.
 - Implement a **New participant**-function where a new folder with log files are created. At the moment a log file is created, or appended to, from where the user executes the commands.
 - Implement a **Connect to remote host**-function for the GUI.
 - Make the GUI able to connect to **remote databases**. At the moment the GUI will read the CSV-data file and build its own, local, MongoDB data base.
 - Look over potential memory leaks in the GUI.










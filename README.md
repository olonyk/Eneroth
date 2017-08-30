# Eneroth  
### Usage:
```sh
Eneroth.py Server [-vlth]
Eneroth.py Dialogue [-th] (--data_file=DB) [--host=HOST] [--ambigthresh=AMBIGTHRESH]
Eneroth.py DummySender [-vth] [--host=HOST] [--nrobj=NROBJ] [--delay=DELAY]
Eneroth.py Ghost [-vth] (--client_type=CLIENT_TYPE) [--host=HOST] 
Eneroth.py GUI [-vtl]
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
  rosrun Eneroth Eneroth.py Server -vlt
  rosrun Eneroth Eneroth.py Dialogue -th --data_file=db.csv --host=192.168.0.100 --ambigthresh=0.5
  rosrun Eneroth Eneroth.py DummySender -vth --host=192.168.0.100 --nrobj=20 --delay=2.0
  rosrun Eneroth Eneroth.py Ghost -vth --client_type=hololens --host=192.168.0.100
  rosrun Eneroth Eneroth.py GUI -vt
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
$ python3.5 Eneroth.py GUI -vt
```
4. In the GUI click on "Connect" and click "Launch".
5. Use the color and shape filters to filter lego parts. Note that the lego parts will show up after a (any) filter is selected.

### Dependencies
1. docopt
2. image (PIL)
3. textblob
4. pymongo
These dependencies can easily be installed by running
```sh
$ pip install docopt image textblob pymongo
```
A Mongo DB service is also needed to be running. Install and run according to [these instructions](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/)

### Todos
 - Don't send all objects when no filters are selected. (Done)
 - On "pick", send "clear" to hololens. (Done)
 - Add safe exit from filter gui. (In progress)
 - Add "point" and "no" buttons to filter gui.
 - Remove restart button from filter gui.
 - Look over potential memory leaks in the GUI.










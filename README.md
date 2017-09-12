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
5. Use the color and shape filters to filter lego parts.
6. To update a position in the lego database base send a message of the following format to the server:
```sh
kernel;update;x_pos1,y_pos1,x_pix1,y_pix1;x_pos1,y_pos1,x_pix1,y_pix1
```
i.e. the name of the reciever, *kernel*, the function, *update*, and one or more tuples of length four with floats, where each tuple is representing a block to be updated. Note that the reciever, function and tuples are separated with semicolons and the tuples are internally separated with commas. The kernel will search for the block in the database with the closest *eucledian* distance from the update coordinates and update its coordinates. For example:

If this is sent to the Server
```sh
kernel;update;0.55,0.41,0.54,0.32
```
... this could be the output from the kernel:
```sh
Updated 4121934 with pos(0.50, 0.40) and pix(?, ?)
                  to pos(0.55, 0.41) and pix(0.54, 0.32)
```

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
 - Look over potential memory leaks in the GUI.










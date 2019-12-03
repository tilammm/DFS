# Simple DFS

## Usage


## Architecture

![](src/DFS.png?raw=true)


## Description of communication protocols

### Initialization
![](src/Initialize.png?raw=true)
```
Initialization is just clearing the tree and deleting all files in the storage node
```

### File write
![](src/Send file.png?raw=true)
```
1.The client tells namenode that it wants to send the file
2.Namenode finds the two most suitable storage node and tells them to open ports
3.Namenode tells the client where to send the file
4.File upload
5.The first storage node sends the file to the next
```

### File read
![](src/Reading.png?raw=true)

```
1.The client tells namenode that it wants to read the file
2.Namenode asks file tree on which nodes the file is stored
3.File tree returns the nodes that store this file
4.Namenode tells the storage node to open port
5.Namenode tells the client where to read the file 
6.Client reads file
```
### Replication
![](src/Replication.png?raw=true)
```
1.Namenode cannot ping storage node
2.Namenode asks the file tree on which nodes the lost files are stored.
3.File tree returns the location of all lost files
4.Namenode orders storage nods to start file sharing
5.Storage nodes sharing files
```


### File manipulation
![](src/File manipulation.png?raw=true)

```
Move / copy / delete operations are similar. First, namenode finds out from file tree on which nodes the file is located.
And then sends a command to these nodes. Upon completion, the file tree is updated.
```
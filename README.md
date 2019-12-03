# Simple DFS

## Usage
1.Install docker-compose:
```
$ sudo apt install docker-compose -y
```
2.Clone the repository and navigate to the repository folder
```
$ git clone https://github.com/tilammm/DFS.git
```
3.For run client:
```
$ python3 client/client.py
```
4.Docker swarm
```
$ docker swarm init
$ docker swarm join --token <token>
```
5.Use deploy/docker-compose.yml at your nodes. 

6.Deploy docker-compose.yml on master node
```
$ docker stack deploy -c docker-compose.yml dfs
```
client side(available commands):
```
1. initialize             Initialize the client storage on a new system
2. file_create "name"     Create a new empty file
3. read "file"            Read any file from DFS (download a file from the DFS to the Client side).
4. write "file"           Put any file to DFS (upload a file from the Client side to the DFS)
5. file_delete "file"     Delete file from DFS
6. file_info "file"       Provide information about the file
7. copy "file" "path"     Create a copy of file 
8. move "file" "path"     Move a file to the specified path
9. open "directory"       It allow to change directory
10. show                  Return list of files and list of directories, which are stored in the directory
11. mkdir "name"          Create a new directory
12. dir_delete "name"     Delete the directory. If the directory contains files the system should ask for confirmation from the user before deletion
```

## Architecture

![](src/DFS.png?raw=true)


## Description of communication protocols

### Initialization
![](src/Initialize.png?raw=true)
```
Initialization is just clearing the tree and deleting all files in the storage node
```

### File write
![](src/Send_file.png?raw=true)
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
![](src/File_manipulation.png?raw=true)

```
Move / copy / delete operations are similar. First, namenode finds out from file tree on which nodes the file is located.
And then sends a command to these nodes. Upon completion, the file tree is updated.
```

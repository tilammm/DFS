import socket
from _thread import *
import threading
import psycopg2
from Name_node.tree import Tree

try:
    connection = psycopg2.connect(user="test",
                                  password="123456",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="DFS")

    cursor = connection.cursor()
    # Print PostgreSQL Connection properties
    print(connection.get_dsn_parameters(), "\n")

    # Print PostgreSQL version
    cursor.execute("SELECT version();")
    record = cursor.fetchone()

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)



buffer_size = 1024
number_of_users = 1
storage_extra_ip = '127.0.0.1'
storage_extra_port = 8100


def login_user(log_in, password):
    query = 'select * from client where username = %s'
    print(log_in)

    cursor.execute(query, (log_in, ))
    users = cursor.fetchall()

    global current_directory
    global file_tree
    current_directory = file_tree

    if len(users) == 0:
        return 0
    else:
        if users[0][2] == password:
            return users[0][0]
        else:
            return 0


def send_file(storage_node_ip, storage_node_port):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((storage_node_ip, storage_node_port))
    message = 'receive:' + storage_extra_ip + ':' + str(storage_extra_port)
    tcp_socket.send(message.encode())
    status = tcp_socket.recv(buffer_size).decode()
    tcp_socket.close()
    if status != 'error':
        return storage_node_ip, status
    else:
        return storage_node_ip


def read_file(storage_node_ip, storage_node_port):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((storage_node_ip, storage_node_port))
    message = 'reading'
    tcp_socket.send(message.encode())
    status = tcp_socket.recv(buffer_size).decode()
    tcp_socket.close()
    if status != 'error':
        return storage_node_ip, status
    else:
        return storage_node_ip


def send_init(storage_node_ip, storage_node_port):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((storage_node_ip, storage_node_port))
    message = 'init'
    tcp_socket.send(message.encode())
    status = tcp_socket.recv(buffer_size).decode()
    tcp_socket.close()
    return status


def mkdir(dir_name, storage_node_ip, storage_node_port):
    # add dir to tree
    global current_directory
    status = current_directory.add_dir(name=dir_name)
    if status != 'ok':
        return status

    # send command to storage node
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((storage_node_ip, storage_node_port))
    message = 'mkdir:' + current_directory.path + dir_name
    tcp_socket.send(message.encode())
    response = tcp_socket.recv(buffer_size).decode()
    tcp_socket.close()
    if response == 'created':
        return 'Directory created: ' + dir_name
    else:
        return 'error'


def filerm(file_name, storage_node_ip, storage_node_port):
    # delete file from tree
    global current_directory
    status = current_directory.delete_file(file_name)

    if status != 'ok':
        return status

    # send command to storage node
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((storage_node_ip, storage_node_port))
    message = 'filerm:' + current_directory.path + file_name
    tcp_socket.send(message.encode())
    response = tcp_socket.recv(buffer_size).decode()
    tcp_socket.close()
    if response == 'removed':
        return 'File deleted: ' + file_name
    else:
        return 'error'


def copy(file_name, dir_name, storage_node_ip, storage_node_port):
    # add dir to tree
    global current_directory
    global file_tree
    candidate = file_tree.get_path_entity(dir_name)

    if candidate is None:
        return 'error'

    new_file = current_directory.get_file(file_name)

    if new_file is None:
        return 'error'

    copied = candidate.add_file(name=new_file.name, size=new_file.size, storage=storage_node_ip)

    # send command to storage node
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((storage_node_ip, storage_node_port))
    global storage_extra_ip, storage_extra_port
    message = 'copy:' + current_directory.path + file_name + ':' + copied.path \
              + ':' + storage_extra_ip + ':' + str(storage_extra_port)
    tcp_socket.send(message.encode())
    response = tcp_socket.recv(buffer_size).decode()
    tcp_socket.close()
    if response == 'copied':
        return 'File copied: ' + copied.name
    else:
        return 'error'


def move(file_name, dir_name, storage_node_ip, storage_node_port):
    # add dir to tree
    global current_directory
    global file_tree
    candidate = file_tree.get_path_entity(dir_name)

    if candidate is None:
        return 'error'

    new_file = current_directory.get_file(file_name)

    if new_file is None:
        return 'error'

    current_directory.delete_file(new_file.name)
    copied = candidate.add_file(name=new_file.name, size=new_file.size, storage=storage_node_ip)

    # send command to storage node
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((storage_node_ip, storage_node_port))
    global storage_extra_ip, storage_extra_port
    message = 'move:' + current_directory.path + file_name + ':' + copied.path \
              + ':' + storage_extra_ip + ':' + str(storage_extra_port)
    tcp_socket.send(message.encode())
    response = tcp_socket.recv(buffer_size).decode()
    tcp_socket.close()
    if response == 'moved':
        return 'File moved: ' + copied.name
    else:
        return 'error'


def delete_dir(storage_node_ip, storage_node_port):
    # delete file from tree
    global current_directory

    if current_directory.parent is None:
        return 'error'

    # send command to storage node
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((storage_node_ip, storage_node_port))
    message = 'del_dir:' + current_directory.path
    tcp_socket.send(message.encode())
    response = tcp_socket.recv(buffer_size).decode()
    tcp_socket.close()
    if response == 'removed':
        current_directory = current_directory.delete_dir()
        return current_directory.path
    else:
        return 'error'


def command_handler(message, conn):
    print(message)
    words = message.split(':')
    storage_node_ip = '127.0.0.1'
    storage_node_port = 8000

    global file_tree
    global current_directory

    if words[0] == 'login':
        out = str(login_user(words[1], words[2]))

    elif words[0] == 'write':
        # add file to tree
        filename = words[1]
        size = words[2]
        current_directory.add_file(name=filename, size=size, storage=[storage_node_ip])
        # opening of port on storage node
        _, storagenode_port = send_file(storage_node_ip, storage_node_port)
        out = storage_node_ip + ':' + storagenode_port

    elif words[0] == 'read':
        storagenode_ip, storagenode_port = read_file(storage_node_ip, storage_node_port)
        out = storagenode_ip + ':' + storagenode_port

    elif words[0] == 'mkdir':
        out = mkdir(words[1], storage_node_ip, storage_node_port)

    elif words[0] == 'copy':
        out = copy(words[1], words[2], storage_node_ip, storage_node_port)

    elif words[0] == 'move':
        out = move(words[1], words[2], storage_node_ip, storage_node_port)

    elif words[0] == 'filerm':
        out = filerm(words[1], storage_node_ip, storage_node_port)

    elif words[0] == 'open':
        out = 'error'
        global file_tree
        if len(words) == 1:
            if current_directory != file_tree:
                current_directory = current_directory.parent
                out = current_directory.path
        else:
            new_dir = current_directory.open(words[1])
            if new_dir is not None:
                current_directory = new_dir
                out = current_directory.path

    elif words[0] == 'show':

        directories = current_directory.get_dirs()
        dirs = ':'
        for dir in directories:
            dirs += dir + ':'

        conn.send(dirs.encode())

        response = conn.recv(1)

        files = current_directory.get_files()
        out = ':'

        for file in files:
            out += file + ':'

    elif words[0] == 'initialize':
        file_tree.delete_dir()
        file_tree = Tree(name='root', path='/home/tilammm/PycharmProjects/DFS/files')
        current_directory = file_tree
        out = send_init(storage_node_ip, storage_node_port)

    elif words[0] == 'dir_delete':
        out = delete_dir(storage_node_ip, storage_node_port)

    else:
        out = 'unknown command'

    return out


def threaded(connection, address):
    while True:
        # data received from client
        data = connection.recv(1024)
        if not data:
            print(f'Connection with {address[0]} closed')
            # lock released on exit
            print_lock.release()
            break

        data = command_handler(data.decode(), connection)
        print(data)
        connection.send(data.encode())
        # connection closed
    connection.close()


if __name__ == '__main__':
    ip = '127.0.0.1'
    port = 5005
    print_lock = threading.Lock()

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((ip, port))
    tcp_socket.listen()

    file_tree = Tree(name='root', path='files/')
    current_directory = file_tree

    while True:
        # establish connection with client
        conn, addr = tcp_socket.accept()

        # lock acquired by client
        print_lock.acquire()
        print(f'Connected to {addr[0]}')

        # Start a new thread and return its identifier
        start_new_thread(threaded, (conn, addr))
    tcp_socket.close()



import operator
import os
import socket
from _thread import *
import threading
from Name_node.tree import Tree
import pickle


storage_list = [['3.134.106.22', 0, True], ['3.17.151.48', 0, True], ['18.217.2.254', 0, True]]


def ping_storage(storage_ip):

    hostname = storage_ip
    response = os.system("ping -c 1 " + hostname)

    # and then check the response...
    if response == 0:
        return True
    else:
        return False


def giveIPs():
    global storage_list
    for i in range(len(storage_list)):
        storage_list[i][2] = ping_storage(storage_list[i][0])
    storage_list.sort(key=operator.itemgetter(1))
    count = 0
    ips = []
    for i in range(len(storage_list)):
        if storage_list[i][2] and count < 2:
            ips.append(storage_list[i])
            count += 1
    return ips[0], ips[1]


buffer_size = 1024
number_of_users = 1


def login_user(log_in, password):

    global current_directory
    global file_tree
    current_directory = file_tree

    if log_in != 'test' or password !='123456':
        return 0
    else:
        return 1


def send_file(storage_node_ip, storage_node_port):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((storage_node_ip, storage_node_port))
    message = 'receive'
    tcp_socket.send(message.encode())
    status = tcp_socket.recv(buffer_size).decode()
    tcp_socket.close()
    if status != 'error':
        return storage_node_ip, status
    else:
        return storage_node_ip


def read_file(filename):
    global current_directory
    file = current_directory.get_file(filename)
    if file is None:
        return 'error', 'error'
    ips = file.storages
    if ping_storage(ips[0]):
        storage_node_ip = ips[0]
    else:
        storage_node_ip = ips[1]
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((storage_node_ip, 8000))
    message = 'reading'
    tcp_socket.send(message.encode())
    status = tcp_socket.recv(buffer_size).decode()
    tcp_socket.close()
    return storage_node_ip, status


def send_init():
    global storage_list
    for i in storage_list:
        if ping_storage(i[0]):
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.connect((i[0], 8000))
            message = 'init'
            tcp_socket.send(message.encode())
            status = tcp_socket.recv(buffer_size).decode()
            tcp_socket.close()
    return 'Initialized'


def mkdir(dir_name):
    # add dir to tree
    global current_directory
    status = current_directory.add_dir(name=dir_name)
    return status


def filerm(file_name):
    # delete file from tree
    global current_directory
    current_file = current_directory.get_file(file_name)
    if(current_file is None):
        return 'error'
    ips = current_file.storages.copy()
    status = current_directory.delete_file(file_name)

    if status != 'ok':
        return status
    response1 = 'removed'
    response2 = 'removed'
    # send command to storage node
    if ping_storage(ips[0]):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((ips[0], 8000))
        message = 'filerm:' + current_directory.path + file_name
        tcp_socket.send(message.encode())
        response1 = tcp_socket.recv(buffer_size).decode()
        tcp_socket.close()

    if ping_storage(ips[1]):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((ips[1], 8000))
        message = 'filerm:' + current_directory.path + file_name
        tcp_socket.send(message.encode())
        response2 = tcp_socket.recv(buffer_size).decode()
        tcp_socket.close()
    if response1 == 'removed' and response2 == 'removed':
        return 'File deleted: ' + file_name
    else:
        return 'error'


def file_creation(file, first_storage, second_storage):
    global current_directory
    message = 'create_file:' + file.path
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((first_storage[0], 8000))
    tcp_socket.send(message.encode())
    tcp_socket.close()

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((second_storage[0], 8000))
    tcp_socket.send(message.encode())
    tcp_socket.close()

    return 'created'


def copy(file_name, dir_name):
    # add dir to tree
    global current_directory
    global file_tree
    candidate = file_tree.get_path_entity(dir_name)

    if candidate is None:
        return 'error'

    current_file = current_directory.get_file(file_name)

    if current_file is None:
        return 'error'

    ping_storage(current_file.storages[0])
    ping_storage(current_file.storages[1])

    copied = candidate.add_file(name=current_file.name, size=current_file.size, storage=current_file.storages)

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((current_file.storages[0], 8000))
    message = 'copy:' + current_directory.path + file_name + ':' + copied.path
    tcp_socket.send(message.encode())
    response1 = tcp_socket.recv(buffer_size).decode()
    tcp_socket.close()

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((current_file.storages[1], 8000))
    message = 'copy:' + current_directory.path + file_name + ':' + copied.path
    tcp_socket.send(message.encode())
    response2 = tcp_socket.recv(buffer_size).decode()
    tcp_socket.close()

    # send command to storage node

    if response1 == 'copied' and response2 == 'copied':
        return 'File copied: ' + copied.name
    else:
        return 'error'


def move(file_name, dir_name):
    # add dir to tree
    global current_directory
    global file_tree
    candidate = file_tree.get_path_entity(dir_name)

    if candidate is None:
        return 'Candidate error'

    current_file = current_directory.get_file(file_name)

    if current_file is None:
        return 'Current file error'

    current_directory.delete_file(current_file.name)
    ping_storage(current_file.storages[0])
    ping_storage(current_file.storages[1])

    copied = candidate.add_file(name=current_file.name, size=current_file.size, storage=current_file.storages)

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((current_file.storages[0], 8000))
    message = 'move:' + current_directory.path + file_name + ':' + copied.path
    tcp_socket.send(message.encode())
    response1 = tcp_socket.recv(buffer_size).decode()
    tcp_socket.close()

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((current_file.storages[1], 8000))
    message = 'move:' + current_directory.path + file_name + ':' + copied.path
    tcp_socket.send(message.encode())
    response2 = tcp_socket.recv(buffer_size).decode()
    tcp_socket.close()

    # send command to storage node

    if response1 == 'moved' and response2 == 'moved':
        return 'File moved: ' + copied.name
    else:
        return 'error'


def delete_dir():
    # delete file from tree
    global current_directory
    global storage_list

    if current_directory.parent is None:
        return 'error'

    for storage in storage_list:
        if(ping_storage(storage[0])):
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.connect((storage[0], 8000))
            message = 'del_dir:' + current_directory.path
            tcp_socket.send(message.encode())
            response = tcp_socket.recv(buffer_size).decode()
            tcp_socket.close()

    # send command to storage node

    current_directory = current_directory.delete_dir()
    return current_directory.path


def command_handler(message, conn):
    print(message)
    words = message.split(':')
    storage_node_port = 8000
    global file_tree
    global current_directory

    first_storage, second_storage = giveIPs()
    if words[0] == 'login':
        out = str(login_user(words[1], words[2]))

    elif words[0] == 'write':
        # add file to tree
        filename = words[1]
        size = words[2]
        first_storage[1] += int(size)
        second_storage[1] += int(size)

        current_directory.add_file(name=filename, size=size, storage=[first_storage[0], second_storage[0]])
        # opening of port on storage node
        _, first_port = send_file(first_storage[0], 8000)
        _, second_port = send_file(second_storage[0], 8000)
        out = first_storage[0] + ':' + first_port + ':' + second_storage[0] + ':' + second_port

    elif words[0] == 'read':
        storagenode_ip, storagenode_port = read_file(words[1])
        if (storagenode_port == 'error'):
            return 'error'
        out = storagenode_ip + ':' + storagenode_port

    elif words[0] == 'mkdir':
        out = mkdir(words[1])

    elif words[0] == 'copy':
        out = copy(words[1], words[2])

    elif words[0] == 'move':
        out = move(words[1], words[2])

    elif words[0] == 'filerm':
        out = filerm(words[1])

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

    elif words[0] == 'file_info':
        file = current_directory.get_file(words[1])
        if file is None:
            return 'error'

        out = file.info()

    elif words[0] == 'file_create':
        file = current_directory.add_file(words[1], size=0, storage=[first_storage[0], second_storage[0]])

        if file is None:
            return 'error'

        out = file_creation(file, first_storage, second_storage)

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
        file_tree = Tree(name='root', path='files/')
        current_directory = file_tree
        out = send_init()

    elif words[0] == 'dir_delete':
        out = delete_dir()

    else:
        out = 'unknown command'

    with open('file_tree.pkl', 'wb') as output:
        pickle.dump(file_tree, output, pickle.HIGHEST_PROTOCOL)

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
    try:
        with open('file_tree.pkl', 'rb') as input:
            file_tree = pickle.load(input)
    except:
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



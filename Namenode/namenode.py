import socket
from _thread import *
import threading
import psycopg2
from Namenode.tree import Tree

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


ip = '127.0.0.1'
port = 5005
buffer_size = 1024
print_lock = threading.Lock()
number_of_users = 1


def login_user(log_in, password):
    query = 'select * from client where username = %s'
    print(log_in)
    cursor.execute(query, (log_in, ))
    users = cursor.fetchall()
    if len(users) == 0:
        return 0
    else:
        return users[0][0]


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


def command_handler(message):
    print(message)
    words = message.split(':')
    storage_node_ip = '127.0.0.1'
    storage_node_port = 8000
    global file_tree
    global current_directory
    if words[0] == 'login':
        out = str(login_user(words[1], words[2]))
    elif words[0] == 'write':
        storagenode_ip, storagenode_port = send_file(storage_node_ip, storage_node_port)
        out = storagenode_ip + ':' + storagenode_port
    elif words[0] == 'read':
        storagenode_ip, storagenode_port = read_file(storage_node_ip, storage_node_port)
        out = storagenode_ip + ':' + storagenode_port
    elif words[0] == 'initialize':
        file_tree.delete_dir()
        file_tree = Tree(name='root', path='/home/tilammm/PycharmProjects/DFS/files')
        current_directory = file_tree
        out = send_init(storage_node_ip, storage_node_port)
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

        data = command_handler(data.decode())
        print(data)
        connection.send(data.encode())
        # connection closed
    connection.close()


if __name__ == '__main__':
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



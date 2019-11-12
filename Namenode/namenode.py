import socket
from _thread import *
import threading
import psycopg2


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


def register_user(login, email, password):
    query = 'INSERT INTO client(client_id, username, password, email) VALUES (%s, %s, %s, %s) RETURNING client_id'
    print(login)
    global number_of_users
    cursor.execute(query, (number_of_users + 1, login, email, password, ))
    user_id = cursor.fetchall()
    number_of_users += 1
    return user_id[0][0]


def login_user(log_in, password):
    query = 'select * from client where username = %s'
    print(log_in)
    cursor.execute(query, (log_in, ))
    users = cursor.fetchall()
    if len(users) == 0:
        return 0
    else:
        return users[0][0]


def send_file():
    storagenode_ip = '127.0.0.1'
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((storagenode_ip, 8080))
    message = 'recive_file'
    tcp_socket.send(message.encode())
    status = tcp_socket.recv(buffer_size).decode()
    tcp_socket.close()
    if status == 'ok':
        return storagenode_ip, 8080
    else:
        return storagenode_ip


def command_handler(message):
    print(message)
    words = message.split(':')
    if words[0] == 'login':
        out = str(login_user(words[1], words[2]))
    elif words[0] == 'register':
        out = str(register_user(words[1], words[2], words[3]))
    elif words[0] == 'write':
        storagenode_ip, storagenode_port = send_file()
        out = storagenode_ip + ':' + str(storagenode_port)
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
    while True:
        # establish connection with client
        conn, addr = tcp_socket.accept()

        # lock acquired by client
        print_lock.acquire()
        print(f'Connected to {addr[0]}')

        # Start a new thread and return its identifier
        start_new_thread(threaded, (conn, addr))
    tcp_socket.close()

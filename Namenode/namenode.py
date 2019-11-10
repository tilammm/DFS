import socket
from _thread import *
import threading


ip = '127.0.0.1'
port = 5005
buffer_size = 1024
print_lock = threading.Lock()


def command_handler(message):
    words = message.split(':')
    command = words[0]
    client_id = words[1]
    file_name = words[2]
    return command


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

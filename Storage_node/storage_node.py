import socket
import sys
import threading
from threading import Thread
from _thread import *
import os
import shutil


files = []
clients = []
print_lock = threading.Lock()
root_directory = 'files/'
ip_extra = ''
port_extra = ''

def send(filename, ip, port):
    f = open(filename, "rb")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect((ip, int(port)))
    sock.sendall(filename.encode())

    print('Waiting for the response...')
    response = sock.recv(1)
    print('Response was received')

    old_file_position = f.tell()
    f.seek(0, os.SEEK_END)
    file_size = f.tell()
    if file_size == 0:
        file_size = 1
    f.seek(old_file_position, os.SEEK_SET)

    bytes_transported = 128

    percent = 0

    byte = f.read(128)

    while byte:

        if bytes_transported * 100 // file_size > percent:
            percent = bytes_transported * 100 // file_size
            if percent > 100:
                percent = 100
            sys.stdout.flush()
            sys.stdout.write(f'\r{percent}%')

        bytes_transported += 128
        sock.send(byte)
        byte = f.read(128)
    print()
    sock.close()
    f.close()





class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    # add 'me> ' to sended message
    def _clear_echo(self, data):
        # \033[F – symbol to move the cursor at the beginning of current line (Ctrl+A)
        # \033[K – symbol to clear everything till the end of current line (Ctrl+K)
        self.sock.sendall('\033[F\033[K'.encode())
        data = 'me> '.encode() + data
        # send the message back to user
        self.sock.sendall(data)

    # broadcast the message with name prefix eg: 'u1> '
    def _broadcast(self, data):
        data = (self.name + '> ').encode() + data
        for u in clients:
            # send to everyone except current client
            if u == self.sock:
                continue
            u.sendall(data)

    # clean up
    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):
        filename = self.sock.recv(128).decode()
        filename = root_directory + filename
        i = 1
        if os.path.isfile(filename):
            while True:
                index = filename.rindex('.')
                if os.path.isfile(filename[:index] + '(Copy_' + str(i) + ')' + filename[index:]):
                    i += 1
                else:
                    filename = filename[:index] + '(Copy_' + str(i) + ')' + filename[index:]
                    break
        with open(filename, 'wb') as f:
            message = f'{filename} created'
            print(message)
            self.sock.send('1'.encode())
            while True:
                # try to read 1024 bytes from user
                # this is blocking call, thread will be paused here
                data = self.sock.recv(128)
                if data:
                    f.write(data)
                else:
                    # if we got no data – client has disconnected
                    self._close()
                    # finish the thread
                    return filename


class ClientReader(Thread):
    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    # add 'me> ' to sended message
    def _clear_echo(self, data):
        # \033[F – symbol to move the cursor at the beginning of current line (Ctrl+A)
        # \033[K – symbol to clear everything till the end of current line (Ctrl+K)
        self.sock.sendall('\033[F\033[K'.encode())
        data = 'me> '.encode() + data
        # send the message back to user
        self.sock.sendall(data)

    # broadcast the message with name prefix eg: 'u1> '
    def _broadcast(self, data):
        data = (self.name + '> ').encode() + data
        for u in clients:
            # send to everyone except current client
            if u == self.sock:
                continue
            u.sendall(data)

    # clean up
    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):
        filename = self.sock.recv(128).decode()
        filename = root_directory + filename
        f = open(filename, 'rb')
        print(f)
        file_size = f.tell()
        print(file_size)
        self.sock.send(str(file_size).encode())

        print('Waiting for the response...')
        receive = self.sock.recv(1)
        print('Response was received')

        with open(filename, 'rb') as f:
            byte = f.read(128)

            while byte:

                self.sock.send(byte)
                byte = f.read(128)
        f.close()
        self._close()
        return


def send_file(storage_node_ip, storage_node_port, storage_node_ip_extra, storage_node_port_extra):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((storage_node_ip, storage_node_port))
    message = 'receive'
    tcp_socket.sendall(message.encode())

    status = tcp_socket.recv(1024).decode()
    tcp_socket.close()
    if status != 'error':
        return storage_node_ip, status
    else:
        return storage_node_ip


def receive(connection):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 0))
    sock.listen()
    connection.send(str(sock.getsockname()[1]).encode())

    print('Server is ready for users')

    next_name = 1

    while True:
        con, addr = sock.accept()
        clients.append(con)
        name = 'u' + str(next_name)
        next_name += 1
        print(str(addr) + ' connected as ' + name)
        print(name, con)
        file_path = ClientListener(name=name, sock=con).start()
        return file_path

def reading(connection):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 0))
    sock.listen()

    connection.send(str(sock.getsockname()[1]).encode())

    print('Server is ready for sending')

    next_name = 1
    while True:
        con, addr = sock.accept()
        clients.append(con)
        name = 'u' + str(next_name)
        next_name += 1
        print(str(addr) + ' connected as ' + name)
        print(name, con)
        ClientReader(name=name, sock=con).start()


def init(conn):
    shutil.rmtree(path=root_directory, ignore_errors=True)
    os.mkdir(root_directory)
    conn.send('Initialized'.encode())
    return 'Initialized'


def command_handler(message, connection):
    print(message)
    isFirst = False
    if(len(message) > 14):
        message, ip_extra, port_extra = message.split(':')
        isFirst = True
    if message == 'receive' and not isFirst:
        receive(connection)
        return 'received'
    elif isFirst:
        file_path = receive(connection)
        _ , storagenode_port_extra = send_file(ip_extra, port_extra)
        send(file_path, ip_extra, storagenode_port_extra)
        return 'received'
    elif message == 'reading':
        reading(connection)
        return 'reading'
    elif message == 'init':
        return init(connection)
    else:
        return 'error'


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
        # connection closed
    connection.close()


if __name__ == '__main__':
    print('Server is ready for commands')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 8000))
    sock.listen()

    while True:
        con, addr = sock.accept()

        start_new_thread(threaded, (con, addr))

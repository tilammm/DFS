import socket
import sys
import threading
from threading import Thread
from _thread import *
import os
import shutil


files = []
clients = []
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
    def __init__(self, name: str, sock: socket.socket, file: str):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name
        self.file = file

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

        filename = self.file
        # correct name
        i = 1
        if os.path.isfile(filename):
            while True:
                index = filename.rindex('.')
                if os.path.isfile(filename[:index] + '(Copy_' + str(i) + ')' + filename[index:]):
                    i += 1
                else:
                    filename = filename[:index] + '(Copy_' + str(i) + ')' + filename[index:]
                    break
        # file receiving
        with open(filename, 'wb') as f:
            message = f'{filename} created'
            print(message)
            self.sock.send(message.encode())
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
                    return


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


def send_file(storage_node_ip, storage_node_port):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((storage_node_ip, int(storage_node_port)))
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

    con, addr = sock.accept()
    clients.append(con)
    name = 'u' + str(next_name)
    next_name += 1
    print(str(addr) + ' connected as ' + name)
    print(name, con)
    filename = con.recv(128).decode()
    ClientListener(name=name, sock=con, file=filename).start()
    print(filename, 'filename')
    return filename


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


def mkdir(dir_name, conn):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    conn.send('created'.encode())
    return 'Created'


def filerm(file_name, conn):
    if os.path.exists(file_name):
        os.remove(file_name)
    conn.send('removed'.encode())
    return 'Removed'


def delete_dir(dir_path, conn):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    conn.send('removed'.encode())
    return 'Removed'


def copy(src, dst, conn):
    shutil.copyfile(src, dst)
    conn.send('copied'.encode())
    return 'Copied'


def command_handler(messages, connection):
    print(messages)

    if messages[0] == 'receive':
        if len(messages) == 1:
            receive(connection)
            return 'received'
        else:
            file_path = receive(connection)
            _, storagenode_port_extra = send_file(messages[1], messages[2])
            send(file_path, messages[1], storagenode_port_extra)
            return 'received'
    elif messages[0] == 'reading':
        reading(connection)
        return 'reading'
    elif messages[0] == 'init':
        return init(connection)
    elif messages[0] == 'mkdir':
        return mkdir(messages[1], connection)
    elif messages[0] == 'filerm':
        return filerm(messages[1], connection)
    elif messages[0] == 'del_dir':
        return delete_dir(messages[1], connection)
    elif messages[0] == 'copy':
        return copy(messages[1], messages[2], connection)
    else:
        return 'error'


def threaded(connection, address):
    while True:
        # data received from client
        data = connection.recv(1024)
        if not data:
            print(f'Connection with {address[0]} closed')
            break
        commands = data.decode().split(':')
        data = command_handler(commands, connection)
        print(data)
    # connection closed
    connection.close()


if __name__ == '__main__':
    print('Server is ready for commands')
    if not os.path.exists('files'):
        os.makedirs('files')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 8000))
    sock.listen()

    while True:
        con, addr = sock.accept()

        start_new_thread(threaded, (con, addr))

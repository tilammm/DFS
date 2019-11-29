import socket
import threading
from threading import Thread
from _thread import *
import os
import shutil


files = []
clients = []
print_lock = threading.Lock()
root_directory = 'Storage_node/files/'


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
                    return


def receive(port, connection):
    connection.send('ok'.encode())

    print('Server is ready for users')

    next_name = 1

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', int(port)))
    sock.listen()

    while True:
        con, addr = sock.accept()
        clients.append(con)
        name = 'u' + str(next_name)
        next_name += 1
        print(str(addr) + ' connected as ' + name)
        print(name, con)
        ClientListener(name=name, sock=con).start()


def init():
    shutil.rmtree(path=root_directory, ignore_errors=True)
    os.mkdir(root_directory)
    return 'Initialized'


def command_handler(message, connection):
    print(message)
    if message == 'receive':
        receive(8800, connection)
        return 'received'
    elif message == 'init':
        return init()
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
        connection.send(data.encode())
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

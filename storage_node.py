import socket
import threading
from threading import Thread
from _thread import *

files = []
clients = []
print_lock = threading.Lock()


class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name
        self.filename_known = False
        self.filename_buffer = ''
        self.final_filename = ''
        self.filedata_buffer = b''

    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):
        while True:

            if not self.filename_known:
                
                name_data = self.sock.recv(1024)
                self.filename_buffer += name_data.decode()
                self.filename_buffer.replace('?', '')

                self.filename_known = True
                print('Filename is ' + self.filename_buffer)
            
                self.sock.sendall('1'.encode())

                if self.filename_buffer in files:

                    print('Collision occured!')
                    i = len(self.filename_buffer) - 1

                    while not self.filename_buffer[i] == '.':
                        if i == 0:
                            break
                        i -= 1
                        
                    file_name = ''
                    file_extension = ''
                        
                    if i == 0:
                        file_name = self.filename_buffer
                        file_extension = ''
                    else:
                        file_name = self.filename_buffer[:i]
                        file_extension = self.filename_buffer[i:]

                    copy_num = 1

                    while (file_name + '_copy' + str(copy_num) + file_extension) in files:
                        copy_num += 1

                    self.final_filename = file_name + '_copy' + str(copy_num) + file_extension

                    files.append(self.final_filename)
                    print('New file name is ' + self.final_filename)
                else:

                    print('No collision occured.')
                    files.append(self.filename_buffer)
                    self.final_filename = self.filename_buffer
            else:

                file_data = self.sock.recv(64)
                
                if file_data:
                    self.filedata_buffer += file_data
                else:

                    current = self.final_filename.split('/')
                    current_file = current[len(current) - 1]
                    f = open(current_file, 'wb+')
                    f.write(self.filedata_buffer)
                    f.close()
                    print('File ' + current_file + ' from ' + self.name + ' was received.')
                    self._close()
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

        ClientListener(name, con).start()


def init():
    return None


def command_handler(message, connection):
    if message == 'receive':
        receive(8800, connection)
        return 'received'
    elif message == 'init':
        init()
        return 'initialized'
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



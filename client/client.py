import socket
import getpass
import os
import sys
import readline

namenode_ip = '127.0.0.1'
namenode_port = 5005
buffer_size = 128


# get filename from filepath
def get_name(filepath):
    subnames = filepath.split('/')

    return subnames.pop()


def send(tcp_sock, filename):
    f = open(filename, "rb")

    file_size = f.tell()
    if file_size == 0:
        file_size = 1

    # sending data  to namenode
    name = get_name(filename)
    message = 'write:' + name + ':' + str(buffer_size)

    tcp_sock.send(message.encode())
    data = tcp_sock.recv(buffer_size).decode()
    storage_node = data.split(':')


    ip = storage_node[0]
    port = storage_node[1]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect((ip, int(port)))

    global current_dir
    name = current_dir + '/' + name
    sock.sendall(name.encode())

    response = sock.recv(128)
    print(response.decode())

    old_file_position = f.tell()
    f.seek(0, os.SEEK_END)
    f.seek(old_file_position, os.SEEK_SET)

    bytes_transported = 128

    percent = 0

    # transfering of data to storagenode
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


def read(filename, ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect((ip, int(port)))

    global current_dir
    path_on_storage = current_dir + '/' + filename
    sock.sendall(path_on_storage.encode())

    print('Waiting for the response...')
    file_size = int(sock.recv(buffer_size))
    print('Response was received')
    if file_size == 0:
        file_size = 1
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
        sock.send('1'.encode())
        bytes_transported = 128
        percent = 0

        while True:

            if bytes_transported * 100 // file_size > percent:
                percent = bytes_transported * 100 // file_size
                if percent > 100:
                    percent = 100
                sys.stdout.flush()
                sys.stdout.write(f'\r{percent}%')

            data = sock.recv(128)
            if data:
                f.write(data)
            else:
                break
            bytes_transported += 128
        print()
        sock.close()
        f.close()
        message = f'{filename} received'
        return message


def log_in():
    nickname = input('Your nickname:')
    password = getpass.getpass(prompt='Your password:')
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((namenode_ip, namenode_port))
    message = 'login:' + nickname + ':' + password
    tcp_socket.send(message.encode())
    data = tcp_socket.recv(buffer_size)
    tcp_socket.close()
    return data


def show(tcp_socket):
    message = 'show'
    tcp_socket.send(message.encode())

    directories = tcp_socket.recv(buffer_size).decode()
    tcp_socket.send('1'.encode())
    files = tcp_socket.recv(buffer_size).decode()

    return directories.replace(':', '   '), files.replace(':', '   ')


def send_command(commands):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((namenode_ip, namenode_port))

    global current_dir

    if commands[0] == 'write':
        send(tcp_socket, commands[1])
        data = 'The file has been sent'

    elif commands[0] == 'read':
        message = commands[0]
        tcp_socket.send(message.encode())
        data = tcp_socket.recv(buffer_size).decode()
        storage_node = data.split(':')
        read(commands[1], storage_node[0], str(storage_node[1]))
        data = 'The file has been read'

    elif commands[0] == 'mkdir':
        message = commands[0] + ':' + commands[1]
        tcp_socket.send(message.encode())
        data = tcp_socket.recv(buffer_size).decode()

    elif commands[0] == 'copy':
        message = commands[0] + ':' + commands[1] + ':' + commands[2]
        tcp_socket.send(message.encode())
        data = tcp_socket.recv(buffer_size).decode()

    elif commands[0] == 'filerm':
        message = commands[0] + ':' + commands[1]
        tcp_socket.send(message.encode())
        data = tcp_socket.recv(buffer_size).decode()
        if data == 'error':
            data = 'Can not remove this file'

    elif commands[0] == 'dir_delete':
        directories, files = show(tcp_socket)
        directories = directories.split()
        files = files.split()

        if len(directories) == 0 and len(files) == 0:
            message = commands[0]
            tcp_socket.send(message.encode())
            data = tcp_socket.recv(buffer_size).decode()
            if data == 'error':
                data = 'Can not remove this directory'
            else:
                current_dir = data[:len(data) - 1]
        else:
            print('Directory is not empty')
            print(f'Directories: {directories}')
            print(f'Files: {files}')
            delete = input(f'Delete directory?(y/n)').lower()
            if delete == 'y':
                message = commands[0]
                tcp_socket.send(message.encode())
                data = tcp_socket.recv(buffer_size).decode()
                if data == 'error':
                    data = 'Can not remove this directory'
                else:
                    current_dir = data[:len(data) - 1]
            else:
                data = 'Directory will not be deleted'

    elif commands[0] == 'initialize':
        current_dir = 'files'
        message = commands[0]
        tcp_socket.send(message.encode())
        data = tcp_socket.recv(buffer_size).decode()

    elif commands[0] == 'open':
        if len(commands) == 2:
            message = commands[0] + ':' + command[1]
        else:
            message = commands[0]
        tcp_socket.send(message.encode())
        data = tcp_socket.recv(buffer_size).decode()
        if data != 'error':
            current_dir = data[:len(data) - 1]  # remove '/'
        else:
            data = 'Can not open this directory'

    elif commands[0] == 'show':
        directories, data = show(tcp_socket)
        print('Directories: ')
        print(directories)

        print('Files:')

    else:
        data = 'unknown command'
    tcp_socket.close()
    return data


def start():
    act = input('Want to login or initialize?(login/initialize): ').lower()
    if act == 'login':
        client_id = log_in()
    elif act == 'initialize':
        print(send_command([act]))
    else:
        print('Unknown command. Try again')
        start()


if __name__ == '__main__':

    sys.stdout.write('\033[1;36m')
    start()

    # Readline сustomization

    readline.parse_and_bind('tab: complete')

    current_dir = 'files'

    while True:
        sys.stdout.write('\033[1;36m')
        command = input(current_dir + ': ').split()
        sys.stdout.write('\033[0;0m')
        print()
        print(send_command(command))
        print()

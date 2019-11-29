import socket
import getpass
import os
import sys
import readline

namenode_ip = '127.0.0.1'
namenode_port = 5005
buffer_size = 128


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


def read(filename, ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect((ip, int(port)))
    sock.sendall(filename.encode())

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


def send_command(commands):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((namenode_ip, namenode_port))
    if commands[0] == 'write':
        message = commands[0]
        tcp_socket.send(message.encode())
        data = tcp_socket.recv(buffer_size).decode()
        storage_node = data.split(':')
        send(commands[1], storage_node[0], str(storage_node[1]))
        data = 'The file has been sent'
    elif commands[0] == 'read':
        message = commands[0]
        tcp_socket.send(message.encode())
        data = tcp_socket.recv(buffer_size).decode()
        storage_node = data.split(':')
        read(commands[1], storage_node[0], str(storage_node[1]))
        data = 'The file has been read'
    elif commands[0] == 'initialize':
        message = commands[0]
        tcp_socket.send(message.encode())
        data = tcp_socket.recv(buffer_size).decode()
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
    start()

    current_dir = 'root'

    # Readline сustomization

    readline.parse_and_bind('tab: complete')

    while True:
        command = input(current_dir + ': ').lower().split()
        print(send_command(command))


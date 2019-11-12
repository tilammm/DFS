import socket
import getpass
import os

namenode_ip = '127.0.0.1'
namenode_port = 5005
buffer_size = 1024


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
    f.seek(old_file_position, os.SEEK_SET)

    i = 1
    buff = b''
    while True:

        byte = f.read(1)

        if byte == b'':
            sock.sendall(buff)
            break
        else:

            if i % 128 == 0:

                hashtags = '#' * int((i / file_size) * 20)
                dots = '.' * (20 - len(hashtags))

                print('\033[F\033[K' + 'Progress: ' + hashtags + dots + ' ', end="\r")
                buff += byte
                sock.sendall(buff)
                buff = b''
                i += 1
            else:
                buff += byte
                i += 1

    print('The file has been sent')

    f.close()


def registration():
    nickname = input('Your nickname:')
    email = input('Your email:')
    password = getpass.getpass(prompt='Your password:')
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((namenode_ip, namenode_port))
    message = 'register:' + nickname + ':' + email + ':' + password
    tcp_socket.send(message.encode())
    data = tcp_socket.recv(buffer_size)
    print(data)
    tcp_socket.close()
    return data.decode()


def log_in():
    nickname = input('Your nickname:')
    password = getpass.getpass(prompt='Your password:')
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((namenode_ip, namenode_port))
    message = 'login:' + nickname + ':' + password
    tcp_socket.send(message.encode())
    data = tcp_socket.recv(buffer_size)
    tcp_socket.close()
    print(data.decode())
    return data


def send_command(commands):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((namenode_ip, namenode_port))
    message = str(client_id)
    for cm in commands:
        message += ':' + cm
    tcp_socket.send(message.encode())
    data = tcp_socket.recv(buffer_size)
    tcp_socket.close()
    return data


if __name__ == '__main__':
    act = input('Want to login or register?(login/register)').lower()
    if act == 'login':
        client_id = log_in()
    elif act == 'register':
        client_id = registration()

    while True:
        command = input().lower().split()
        print(send_command(command).decode())

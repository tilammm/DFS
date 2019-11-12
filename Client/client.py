import socket
import getpass

namenode_ip = '127.0.0.1'
namenode_port = 5005
buffer_size = 1024


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

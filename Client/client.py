import socket

namenode_ip = '127.0.0.1'
namenode_port = 5005
client_id = 1
buffer_size = 1024


def send_command(commands):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((namenode_ip, namenode_port))
    message = commands[0] + ':' + str(client_id) + ':' + commands[1]
    tcp_socket.send(message.encode())
    data = tcp_socket.recv(buffer_size)
    tcp_socket.close()
    return data


if __name__ == '__main__':
    while True:
        command = input().lower().split()
        print(send_command(command).decode())

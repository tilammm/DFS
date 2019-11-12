import os
import sys
import socket


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


# if __name__ == '__main__':
#     send('/home/kamil/Desktop/Innopolis/bs-3/distributed_systems/labs/lab6/qwe.jpg', 'localhost', '8800')


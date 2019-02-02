import socket

HOST = '192.168.101.111'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

def client():
    while True:
        try:
            content = input(':')
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                s.sendall(bytes(content,encoding="utf-8"))
                data = s.recv(1024)
            print('Received', repr(data))
        except ConnectionResetError:
            print('ConnectionResetError, restarting.')
            client()

client()
        

import socket

HOST = '192.168.101.111'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

def server():
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, PORT))
                s.listen()
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)
                    while True:
                        data = conn.recv(512)
                        if not data:
                            break
                        conn.sendall(data)
                        gpio_status = data.decode(encoding='utf-8')
                        print(gpio_status)
                        if gpio_status == '1':
                            print('led on')
                        elif gpio_status == '0':
                            print('led off')
                        else:
                            print('error gpio status')
        except ConnectionResetError:
            print('ConnectionResetError, restarting.')
            server()

server()


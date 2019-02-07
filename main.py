import socket
import time
import network
from machine import Pin
    
#检测网络是否已连接
wlan = network.WLAN(network.STA_IF)
while True:
    if len(wlan.ifconfig()[0]) > 7:
        print(wlan.ifconfig()[0])
        break
    else:
        print('waiting for wirelss connected')
        print(wlan.ifconfig()[0])
        time.sleep(1)
ip = str(wlan.ifconfig()[0])

def server():
    #socket服务端，接收数据来操作继电器
    try:
        while True:
            s = socket.socket()
            ai = socket.getaddrinfo(ip, 80)
            print("Bind address info:", ai)
            addr = ai[0][-1]
            
            #防止出现reuseraddr的错误
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            s.bind(addr)
            s.listen(5)
            print("Listening: {}:80, standing by.".format(ip))
            #开始循环接收
            while True:
                res = s.accept()
                client_s = res[0]
                client_addr = res[1]
                print("From:", client_addr)
                #print("Client socket:", client_s)
                req = client_s.recv(512)
                #req为bytes的format格式，发送pin的value
                #2为pin端口号
                p_n = Pin(2, Pin.OUT)
                #根据状态执行操作，数值可能会反
                if req == b'1':
                    pow_s = 'power on'
                    p_n.on()
                elif req == b'0':
                    pow_s = 'power off'
                    p_n.off()
                else:
                    pow_s = 'error'
                    print('error request')
                print('<<<{}<<<'.format(pow_s), req) 

                client_s.send(b'standing by\nserver gpio status: %s' % p_n.value())
                client_s.close()
    except OSError:
        time.sleep(1)
        server()

def client():
    try:
        #led server ip address
        s_ip = '192.168.101.111'
        #定义gpio的pin为输入
        n = 16
        p_nu = Pin(n, Pin.IN)
        #记录pin的旧value
        p_nu_v = p_nu.value()
        content = b'%s'
        print('First check gpio{} value is {}'.format(n, p_nu_v))
        #执行首次发送
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((s_ip, 80))
        print('First power switch {}'.format(p_nu_v))
        s.send(content % p_nu_v)
        data = s.recv(1024)
        print('Received', repr(data))
        s.close()
        #执行状态检测并发送
        while True:
            #新旧value对比，避免频繁发送数据
            if p_nu_v == p_nu.value():
                print('>>gpio value not change, standing by {}'.format(p_nu_v))
                time.sleep(1)
            else:
                s = socket.socket()
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.connect((s_ip, 80))
                p_nu_v = p_nu.value()
                print('<<gpio value changed {}, power switch!'.format(p_nu_v))
                s.send(content % p_nu_v)
                data = s.recv(1024)
                print('Received', repr(data))
                s.close()
    except OSError:
            time.sleep(1)
            client()

server()

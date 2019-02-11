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
                print('<<<', req) 
                if req == b'1':
                    p_n.on()
                elif req == b'0':
                    p_n.off()
                else:
                    pass
                client_s.send(b'standing by\nserver gpio status: %s' % p_n.value())
                client_s.close()
    except OSError:
        time.sleep(1)
        server()

def notice_led(v):
    #led指示灯函数
    led = Pin(16, Pin.OUT)
    if v == 0:
        print('power on, standing by')
        led.on()
    elif v == 1:
        print('power off, standing by')
        led.off()
    else:
        pass

def client():
    #pin14为输入，pin16为指示灯输出
    try:
        #led server ip address
        s_ip = '192.168.101.111'
        #定义gpio的pin为输入
        button = Pin(14, Pin.IN, Pin.PULL_UP)
        #记录gpio初始value此处参见这里的解释：
        # The value function returns the current level of the pin,
        # either 1 for a high logic level or 0 for a low logic level.
        # Notice how the button is at a high level (value returns 1) when
        # it's not pressed. This is because the pull-up resistor keeps the pin at
        # a high level when it's not connected to ground through the button.
        # When the button is pressed then the input pin connects to ground
        # and reads a low level (value returns 0).
        button_v = button.value()
        content = b'%s'
        print('First check gpio 14 value is {}'.format(button_v))
        #执行首次发送
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #设置socket超时时间
        s.settimeout(5)
        s.connect((s_ip, 80))
        s.settimeout(None)
        print('First power switch {}'.format(button_v))
        s.send(content % button_v)
        data = s.recv(1024)
        print('Received', repr(data))
        s.close()
        notice_led(button_v)
        #执行状态检测并发送
        while True:
            #新旧value对比，避免频繁发送数据
            if button_v == button.value():
                time.sleep(0.5)
                pass                
            else:
                s = socket.socket()
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.settimeout(5)
                s.connect((s_ip, 80))
                s.settimeout(None)
                button_v = button.value()
                print('<<gpio value changed {}, turn on switch!'.format(button_v))
                s.send(content % button_v)
                data = s.recv(1024)
                print('Received', repr(data))
                s.close()
                notice_led(button_v)
    except (OSError) as Argument:
        print(Argument)
        time.sleep(1)
        client()

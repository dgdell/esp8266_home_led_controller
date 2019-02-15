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
                    p_n.off()
                elif req == b'0':
                    p_n.on()
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
    if v == '0':
        print('power on, standing by')
        led.on()
    elif v == '1':
        print('power off, standing by')
        led.off()
    else:
        pass

def socket_send(button_v):
    #socket发送数据函数
    #led server ip address
    s_ip = '192.168.137.1'
    content = b'%s'
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #设置socket超时时间
    s.settimeout(5)
    s.connect((s_ip, 80))
    s.settimeout(None)
    print('turn on power switch {}'.format(content % button_v))
    s.send(content % button_v)
    data = s.recv(1024)
    #print('Received', repr(data))
    s.close()
    notice_led(button_v)
    
def client():
    notice_led('1')
    #定义gpio的pin为输入
    #默认高电平，button.value()=1，led灯服务器接收为关闭
    button = Pin(14, Pin.IN, Pin.PULL_UP)
    #pin14为输入，pin16为指示灯输出
    button_s = 'up'
    light = 'off'
    while True:    
        try:
            if (button_s =='up' and light =='off'):
                #按钮按下之前的状态
                if not button.value():
                    socket_send('0')
                    button_s = 'down'
                    light = 'on'
            elif (button_s =='down' and light =='on'):
                #stay in this state until button release
                if button.value():
                    button_s = 'up'
            elif (button_s =='up' and light =='on'):
                if not button.value():
                    socket_send('1')
                    button_s = 'down'
                    light = 'off'
            elif (button_s =='down' and light =='off'):
                if button.value():
                    button_s = 'up'
            time.sleep(0.1)
     
        except (OSError) as Argument:
            print(Argument)
            time.sleep(1)
            client()

client()

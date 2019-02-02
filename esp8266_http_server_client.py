def do_connect(ssid, pswd):
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, pswd)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

def do_ntp():
    import ntptime
    ntptime.settime()

def gpio_c(sw):
    #gpio电平控制函数
    from machine import Pin
    #gpio端口号，连接到继电器
    n = 2
    p_n = Pin(n, Pin.OUT)
    #根据状态执行操作，数值可能会反
    if sw == "1":
        p_n.on()
    elif sw == "0":
        p_n.off()
    else:
        print('wrong gpio status.')

#灯泡电源控制函数（开机-连接网络-循环（获取远程开关的状态-执行操作））
def light_power_controller():
    import urequests
    import network
    import time
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
    while True:
        #初次检测控制器gpio的状态
        #url为开关的ip地址
        url = "http://192.168.137.1:8000"
        print('first check')
        response = urequests.get(url)
        t = response.text
	print(t)
        gpio_c(t)
        response.close()
        time.sleep(0.8)
        while True:
            response = urequests.get(url)
            if response.text == t:
                #和新数值比较，如果相同，不再触发gpio电平
                print('>>>>gpio NO change: {}'.format(response.text))
                time.sleep(0.8)
            else:
                print('<<<<gpio change: {}'.format(response.text))
                gpio_c(response.text)
                #gpio旧状态变量重新赋值
                o = response.text
                time.sleep(0.8)
            response.close()

#开关函数，一个简单的webserver，根据开关的gpio value，传入到web的content 
def switch_server():
    import socket
    import network
    import time
    from machine import Pin

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
    #定义gpio的pin为输入
    n = 2
    p_nu = Pin(n, Pin.IN)
    
    #CONTENT的第一行必须要加入 %a代表字符串 %d数值 参见：https://mail.python.org/pipermail/python-dev/2014-March/133621.html
    CONTENT = b"""\
    HTTP/1.1 200 OK\nConnection: close\nServer: ESP8266-pyboard\nContent-Type: text/html\n\n
    %a
    """
    s = socket.socket()
    ai = socket.getaddrinfo(ip, 80)
    print("Bind address info:", ai)
    addr = ai[0][-1]

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(addr)
    s.listen(5)
    print("Listening, connect your browser to http://{}".format(ip))
    while True:
        res = s.accept()
        client_s = res[0]
        client_addr = res[1]
        print("Client address:", client_addr)
        print("Client socket:", client_s)
        req = client_s.recv(4096)
        print("Request:")
        print(req)
        #bytes的format格式，发送pin的value
        g_s = Pin(n, Pin.IN)
        client_s.send(CONTENT % g_s)
        client_s.close()



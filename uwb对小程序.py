#使用MicroPython 对ESP32C3编写代码，根据已知的标签对4个基站的距离计算出标签的3维坐标,并print出来坐标
import math
import time
import uos  #用于split（）方法切割字符

import socket # udp网络功能
import network # 入网功能

import machine
uart = machine.UART(1, baudrate=115200, tx=0, rx=1)  # 初始化UART，设置波特率和引脚 tx=0, rx=1  17 18

len_distances_str = 0
distances_0_str = 0
distances_1_str = 0
distances_2_str = 0
distances_3_str = 0

# 假设已知的距离和基站坐标信息
distances = [0, 0, 0, 0]  # 标签到四个基站的距离  53, 59, 52, 45 distances_0, distances_1, distances_2, distances_3

stations = [(20, 0, 0), (0, 20, 0), (0, 0, 0), (20, 20, 5)]  # 四个基站的坐标      

Tag_x_y_z = [0, 0, 0]


def trilateration(distances, stations):
    x1, y1, z1 = stations[0]
    x2, y2, z2 = stations[1]
    x3, y3, z3 = stations[2]
    x4, y4, z4 = stations[3]
    
    d1, d2, d3, d4 = distances
    
    A = 2 * (x2 - x1)
    B = 2 * (y2 - y1)
    C = 2 * (z2 - z1)
    D = 2 * (x3 - x1)
    E = 2 * (y3 - y1)
    F = 2 * (z3 - z1)
    G = 2 * (x4 - x1)
    H = 2 * (y4 - y1)
    I = 2 * (z4 - z1)
    
    J = math.pow(x2, 2) - math.pow(x1, 2) + math.pow(y2, 2) - math.pow(y1, 2) + math.pow(z2, 2) - math.pow(z1, 2) + math.pow(d1, 2) - math.pow(d2, 2)
    K = math.pow(x3, 2) - math.pow(x1, 2) + math.pow(y3, 2) - math.pow(y1, 2) + math.pow(z3, 2) - math.pow(z1, 2) + math.pow(d1, 2) - math.pow(d3, 2)
    L = math.pow(x4, 2) - math.pow(x1, 2) + math.pow(y4, 2) - math.pow(y1, 2) + math.pow(z4, 2) - math.pow(z1, 2) + math.pow(d1, 2) - math.pow(d4, 2)
    
    M = A*(E*I - H*F) - B*(D*I - G*F) + C*(D*H - G*E)
    
    x = (J*(E*I - H*F) - B*(K*I - L*F) + C*(K*H - L*E)) / M
    y = (A*(K*I - L*F) - J*(D*I - G*F) + C*(D*L - G*K)) / M
    z = (A*(E*L - H*K) - B*(D*L - G*K) + J*(D*H - G*E)) / M

    Tag_x_y_z[0] = x
    Tag_x_y_z[1] = y
    Tag_x_y_z[2] = z
    return x, y, z


      
def uart_rece(uart):
    received_data = "" # 初始化一个空字符串用于存储接收的数据
    num_int = 0
    data_count = 0  # 已接收数据的数量
    
    while True:
        if uart.any():  # 检查是否有数据可读取
            data = uart.read(1)  # 读取所有可用数据 
            
            #print(data)
            received_data += data.decode('utf-8')
            data_count+=1
            #print("received_data :",received_data)
                
            if data_count >= 2:
                # 示例代码：将接收到的数据转换为整数
                if data_count == 2:
                    try:
                        num_int = int(received_data)
                    except ValueError:
                        print("无法将接收到的数据转换为整数")
                    
                if data_count == num_int+1:  # 81 5900 5200 4500 //18个
                    print("data_count :",data_count)
                    print("received_data :",received_data)
                    len_distances_str,distances_0_str,distances_1_str,distances_2_str,distances_3_str = [i for i in received_data.split()]
                        
                    distances[0] = int(distances_0_str)/1000 #int(distances_0_str)
                    distances[1] = int(distances_1_str)/1000 #int(distances_1_str)
                    distances[2] = int(distances_2_str)/1000 #int(distances_2_str)
                    distances[3] = int(distances_3_str)/1000 #int(distances_3_str)
                    #TEMP = int(distances_4_str)
                    #HUM  = int(distances_5_str)
                    
                    data_count=0
                    received_data = "" #
                    
                    time.sleep(0.1)
                    break 

#begin====================UDP=============================UDP===========================UDP=======================
# 连接wifi
def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    wlan.active(True)
    wlan.ifconfig(("192.168.142.110", "255.255.255.0", "192.168.0.1", "8.8.8.8"))
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('a','12345678')# 填写wifi信息  'Redmi K40 Gaming LHX','lhx123123.'
        
        i = 1
        while not wlan.isconnected():
            print("正在链接...{}".format(i))
            i += 1
            time.sleep(0.8)
    print('network config:', wlan.ifconfig())# 打印入网ip信息

# 启动网络功能（UDP）
def send_udp(send_ip):
    
    udp_s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# 创建udp接收data数据  
    addr = ((send_ip, 8080)) #  绑定端口号
    print("udp send addr:",addr)
    
    #char_list = [str(round(Tag_x_y_z[0])), str(round(Tag_x_y_z[1])), str(round(Tag_x_y_z[2]))]
    char_list = [str(Tag_x_y_z[0]), str(Tag_x_y_z[1]), str(Tag_x_y_z[2])]
    
    print("tag_x:",Tag_x_y_z[0])
    print("tag_y:",Tag_x_y_z[1])
    print("tag_z:",Tag_x_y_z[2])
    
    send_data = ' '.join(char_list)
    print("udp send data:",send_data)
    # 发起请求
    udp_s.sendto(send_data.encode('utf-8'), addr)   
    udp_s.close()
    
def rece_udp():
    udp_r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 创建udp接收data数据  
    udp_r.bind(("192.168.142.110", 8080)) #  绑定端口号
    print("success")
    return udp_r

#end====================UDP=============================UDP===========================UDP=======================

def main():    
    do_connect() # 连接wifi    
    udp_socket = rece_udp() # 创建UDP      
    while True:
        
        #接受UDP的指令
        recv_data, recv_info = udp_socket.recvfrom(1024)  # 接收网络数据
        print("{}发送{}".format(recv_info, recv_data))# 将接收的数据串口打印
        recv_data_str = recv_data.decode("utf-8")
        
        #接受串口的距离数据，计算位置坐标
        uart_rece(uart)
        tag_x, tag_y, tag_z = trilateration(distances, stations)
        print("Tag's 3D position: ({}, {}, {})".format(tag_x, tag_y, tag_z))   #Tag's 3D position: (3.05, 2.2, 3.8)
        
        #UDP发送数据
        if 'request' in recv_data_str:
            try:
                #print(recv_data_str)
                send_udp(recv_info[0])
                time.sleep(2)
            except Exception as ret:
                print("error:", ret) 
        

if __name__ == "__main__":
    main()
   
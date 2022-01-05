"""
@ author: xujie ZHONG
@ tools: pycharm
@ content: 实现隔离变压器远程移相，缺相，调频，调压
@ date: 2020.8.25
@ email: 18201989787@163.com
"""

import tkinter
import serial
import serial.tools.list_ports
from tkinter import messagebox
from math import sqrt

command_list = {"停止": "7B 00 08 01 0F 00 18 7D",
                "启动": "7B 00 08 01 0F FF 17 7D",
                "移相ABC": "7B 00 09 01 5A 40 00 A4 7D",
                "移相ACB": "7B 00 09 01 5A 40 01 A5 7D",
                "移相BAC": "7B 00 09 01 5A 40 02 A6 7D",
                "移相BCA": "7B 00 09 01 5A 40 03 A7 7D",
                "移相CAB": "7B 00 09 01 5A 40 04 A8 7D",
                "移相CBA": "7B 00 09 01 5A 40 05 A9 7D",
                "缺相A": "7B 00 09 01 5A 40 06 AA 7D",
                "缺相B": "7B 00 09 01 5A 40 07 AB 7D",
                "缺相C": "7B 00 09 01 5A 40 08 AC 7D"
                }


def uchar_checksum(data, byteorder='little'):
    """
    uchar_checksum 按字节计算校验和。每个字节被翻译为无符号整数
    :param data: 字节串
    :param byteorder: 大小端
    """
    length = len(data)
    checksum = 0
    for i in range(0, length):
        checksum += int.from_bytes(data[i:i + 1], byteorder, signed=False)
        checksum &= 0xFF  #
    return checksum


def cal_command(freq, value):
    """
    cal_command 计算调压调频命令
    :param freq: 频率
    :param value: 电压
    计算方法 频率*100，再转换为16进制，得到一个四位数，对应命令中的两个数据为
    线电压*10，除以根号3得到相电压，再转换为16进制，也得到一个四位数，对应命令中的两个数据位
    """
    freq = int(freq * 100)  # 频率*100
    value = int(value * 10 / sqrt(3))  # 电压*100/根号3
    freq = hex(freq)  # 将10进制数转换为16进制
    freq = freq.replace("0x", "")  # hex得到的16进制前缀为0x，需要去掉
    value = hex(value)  # 将10进制数转换为16进制
    value = value.replace("0x", "")  # hex得到的16进制前缀为0x，需要去掉
    value = value.rjust(4, '0')  # 转换得到的16进制数前面补0得到一个四位数
    freq = freq.rjust(4, '0')  # 转换得到的16进制数前面补0得到一个四位数
    freq1 = freq[0:2]  # 四位数的前两位对应一个数据位
    freq2 = freq[2:4]  # 四位数的后两位对应一个数据位
    value1 = value[0:2]  # 四位数的前两位对应一个数据位
    value2 = value[2:4]  # 四位数的后两位对应一个数据位
    # 将数据位放入命令中
    str1 = "00 0E 01 5A 50 00 00 {} {} {} {}".format(value1, value2, freq1, freq2)
    str1 = str1.upper()    # 转换为大写
    # print(str1)
    packet = bytes.fromhex(str1)  # 将十六进制转化为二进制
    # print(packet)
    check = uchar_checksum(packet, byteorder='little')  # 计算校验和
    # print(check)
    check = hex(check)  # 将校验和转化为十六进制
    check = check.replace("0x", "")  # 去掉0x前缀
    check.rjust(2, '0')  # 转换得到的16进制数前面补0得到一个二位数
    check = check.upper() # 转化为大写
    command = "7B" + " " + str1 + " " + check + " " + "7D"  # 加上首部，尾部
    return command


class Communication:
    # 初始化
    def __init__(self, com, bps, timeout):
        self.port = com
        self.bps = bps
        self.timeout = timeout
        global Ret
        try:
            # 打开串口，并得到串口对象
            self.main_engine = serial.Serial(self.port, self.bps, timeout=self.timeout)
            if self.main_engine.is_open:
                Ret = True
                print(messagebox.showinfo(title="消息提示", message="连接成功"))
        except:
            print(messagebox.showinfo(title="消息提示", message="连接失败，请确认端口号为COM4，机器波特率为38400"))

    # 打印设备基本信息
    def Print_Name(self):
        print(self.main_engine.name)  # 设备名字
        print(self.main_engine.port)  # 读或者写端口
        print(self.main_engine.baudrate)  # 波特率
        print(self.main_engine.bytesize)  # 字节大小
        print(self.main_engine.parity)  # 校验位
        print(self.main_engine.stopbits)  # 停止位
        print(self.main_engine.timeout)  # 读超时设置
        print(self.main_engine.writeTimeout)  # 写超时
        print(self.main_engine.xonxoff)  # 软件流控
        print(self.main_engine.rtscts)  # 软件流控
        print(self.main_engine.dsrdtr)  # 硬件流控
        print(self.main_engine.interCharTimeout)  # 字符间隔超时

    # 验证串口是否打开
    def is_open_engine(self):
        return self.main_engine.is_open

    # 打开串口
    def Open_Engine(self):
        self.main_engine.open()

    # 关闭串口
    def Close_Engine(self):
        self.main_engine.close()
        print(self.main_engine.is_open)  # 检验串口是否打开

    # 打印可用串口列表
    @staticmethod
    def Print_Used_Com():
        port_list = list(serial.tools.list_ports.comports())
        print(port_list)

    # 接收指定大小的数据
    # 从串口读size个字节。如果指定超时，则可能在超时后返回较少的字节；如果没有指定超时，则会一直等到收完指定的字节数。
    def Read_Size(self, size):
        return self.main_engine.read(size=size)

    # 接收一行数据
    # 使用readline()时应该注意：打开串口时应该指定超时，否则如果串口没有收到新行，则会一直等待。
    # 如果没有超时，readline会报异常。
    def Read_Line(self):
        return self.main_engine.readline()

    # 发数据
    def Send_data(self, data):
        self.main_engine.write(data)
        print(data)

    # 更多示例
    # self.main_engine.write(chr(0x06).encode("utf-8"))  # 十六制发送一个数据
    # print(self.main_engine.read().hex())  #  # 十六进制的读取读一个字节
    # print(self.main_engine.read())#读一个字节
    # print(self.main_engine.read(10).decode("gbk"))#读十个字节
    # print(self.main_engine.readline().decode("gbk"))#读一行
    # print(self.main_engine.readlines())#读取多行，返回列表，必须匹配超时（timeout)使用
    # print(self.main_engine.in_waiting)#获取输入缓冲区的剩余字节数
    # print(self.main_engine.out_waiting)#获取输出缓冲区的字节数
    # print(self.main_engine.readall())#读取全部字符。

    # 接收数据
    # 一个整型数据占两个字节
    # 一个字符占一个字节

    def Recive_data(self, way):
        # 循环接收数据，此为死循环，可用线程实现
        print("开始接收数据：")
        while True:
            try:
                if self.main_engine.in_waiting:
                    # 一个字节一个字节的接收
                    if way == 0:
                        for i in range(self.main_engine.in_waiting):
                            print("接收ascii数据：" + str(self.Read_Size(1)))
                            data1 = self.Read_Size(1).hex()  # 转为十六进制
                            print("接受十六进制数据：" + data1)
                            data2 = int(data1, 16)
                            print("收到数据十六进制：" + data1 + "  收到数据十进制：" + str(data2))
                    # 整体接收
                    if way == 1:
                        # data = self.main_engine.read(self.main_engine.in_waiting).decode("utf-8")#方式一
                        data = self.main_engine.read_all()
                        print("接收ascii数据：", data)
            except Exception:
                print("异常报错：")


class MainSerial:
    def __init__(self):
        # 定义串口变量
        self.port = "COM4"  # 端口号，内置为COM4
        self.band = 38400  # 波特率，内置为38400
        self.check = 1  # 校验位，默认为1
        self.data = 8  # 数据位，默认为8
        self.stop = 1  # 停止位，默认为1
        self.freq = None  # 频率变量
        self.my_serial = None  # 串口变量

        # 频率电压变量
        self.freq = None
        self.volt = 380

        # 初始化窗体
        self.mainwin = tkinter.Tk()
        self.mainwin.title("隔离变压器串口调试工具")
        self.mainwin.geometry("600x350")

        # 文本标签
        self.label1 = tkinter.Label(self.mainwin, text="移相", font=("宋体", 13))
        self.label1.place(x=250, y=10)
        # 文本标签
        self.label2 = tkinter.Label(self.mainwin, text="缺相", font=("宋体", 13))
        self.label2.place(x=400, y=10)
        # # 文本标签
        # self.label3 = tkinter.Label(self.mainwin, text="自动", font=("宋体", 13))
        # self.label3.place(x=400, y=180)
        # 文本标签
        self.label4 = tkinter.Label(self.mainwin, text="状态", font=("宋体", 13))
        self.label4.place(x=250, y=300)
        # 文本标签
        self.label5 = tkinter.Label(self.mainwin, text="频率(Hz)", font=("宋体", 13))
        self.label5.place(x=20, y=180)
        # 文本标签
        self.label6 = tkinter.Label(self.mainwin, text="电压(V)", font=("宋体", 13))
        self.label6.place(x=20, y=220)
        # # 文本标签
        # self.label7 = tkinter.Label(self.mainwin, text="等待时间(s)", font=("宋体", 13))
        # self.label7.place(x=400, y=250)

        # connect按键
        self.button_connect = tkinter.Button(self.mainwin, text="连接",
                                             command=self.button_connect_click, font=("宋体", 13),
                                             width=10, height=1)
        self.button_connect.place(x=40, y=45)  # 显示控件

        # start按键
        self.button_start = tkinter.Button(self.mainwin, text="启动",
                                           command=self.button_start_click, font=("宋体", 13),
                                           width=10, height=1)
        self.button_start.place(x=40, y=85)  # 显示控件

        # stop按键
        self.button_stop = tkinter.Button(self.mainwin, text="停止",
                                          command=self.button_stop_click, font=("宋体", 13),
                                          width=10, height=1)
        self.button_stop.place(x=40, y=125)  # 显示控件

        # ABC按键
        self.button_ABC = tkinter.Button(self.mainwin, text="ABC",
                                         command=self.button_ABC_click, font=("宋体", 13),
                                         width=10, height=1)
        self.button_ABC.place(x=250, y=45)  # 显示控件

        # ACB按键
        self.button_ACB = tkinter.Button(self.mainwin, text="ACB",
                                         command=self.button_ACB_click, font=("宋体", 13),
                                         width=10, height=1)
        self.button_ACB.place(x=250, y=85)  # 显示控件

        # BAC按键
        self.button_BAC = tkinter.Button(self.mainwin, text="BAC",
                                         command=self.button_BAC_click, font=("宋体", 13),
                                         width=10, height=1)
        self.button_BAC.place(x=250, y=125)  # 显示控件

        # BCA按键
        self.button_BCA = tkinter.Button(self.mainwin, text="BCA",
                                         command=self.button_BCA_click, font=("宋体", 13),
                                         width=10, height=1)
        self.button_BCA.place(x=250, y=165)  # 显示控件

        # CAB按键
        self.button_CAB = tkinter.Button(self.mainwin, text="CAB",
                                         command=self.button_CAB_click, font=("宋体", 13),
                                         width=10, height=1)
        self.button_CAB.place(x=250, y=205)  # 显示控件

        # CBA按键
        self.button_CBA = tkinter.Button(self.mainwin, text="CBA",
                                         command=self.button_CBA_click, font=("宋体", 13),
                                         width=10, height=1)
        self.button_CBA.place(x=250, y=245)  # 显示控件

        # A按键
        self.button_A = tkinter.Button(self.mainwin, text="A",
                                       command=self.button_A_click, font=("宋体", 13),
                                       width=10, height=1)
        self.button_A.place(x=400, y=45)  # 显示控件

        # B按键
        self.button_B = tkinter.Button(self.mainwin, text="B",
                                       command=self.button_B_click, font=("宋体", 13),
                                       width=10, height=1)
        self.button_B.place(x=400, y=85)  # 显示控件

        # C按键
        self.button_C = tkinter.Button(self.mainwin, text="C",
                                       command=self.button_C_click, font=("宋体", 13),
                                       width=10, height=1)
        self.button_C.place(x=400, y=125)  # 显示控件

        # # 自动按键
        # self.button_auto = tkinter.Button(self.mainwin, text="auto",
        #                                   command=self.button_auto_click, font=("宋体", 13),
        #                                   width=10, height=1)
        # self.button_auto.place(x=400, y=210)  # 显示控件

        # 电压频率确认按键
        self.button_confirm = tkinter.Button(self.mainwin, text="设置",
                                             command=self.button_confirm_click, font=("宋体", 13),
                                             width=10, height=1)
        self.button_confirm.place(x=90, y=300)  # 显示控件

        # 频率按键1，50Hz
        self.button_freq1 = tkinter.Button(self.mainwin, text="50",
                                           command=self.button_freq1_click, font=("宋体", 13),
                                           width=4, height=1)
        self.button_freq1.place(x=90, y=180)  # 显示控件

        # 频率按键2，60Hz
        self.button_freq2 = tkinter.Button(self.mainwin, text="60",
                                           command=self.button_freq2_click, font=("宋体", 13),
                                           width=4, height=1)
        self.button_freq2.place(x=150, y=180)  # 显示控件

        # 电压按键1，380V
        self.button_volt1 = tkinter.Button(self.mainwin, text="380",
                                           command=self.button_volt1_click, font=("宋体", 13),
                                           width=4, height=1)
        self.button_volt1.place(x=90, y=220)  # 显示控件

        # 电压按键2，418V
        self.button_volt2 = tkinter.Button(self.mainwin, text="418",
                                           command=self.button_volt2_click, font=("宋体", 13),
                                           width=4, height=1)
        self.button_volt2.place(x=150, y=220)  # 显示控件

        # 电压上键，每次按下电压加0.1V
        self.button_volt_up = tkinter.Button(self.mainwin, text="+",
                                             command=self.button_voltup_click, font=("宋体", 13),
                                             width=2, height=1)
        self.button_volt_up.place(x=180, y=260)  # 显示控件

        # 电压下键，每次按下电压减0.1V
        self.button_volt_down = tkinter.Button(self.mainwin, text="-",
                                               command=self.button_voltdown_click, font=("宋体", 13),
                                               width=2, height=1)
        self.button_volt_down.place(x=90, y=260)  # 显示控件

        # 电压值显示框
        self.VoltView = tkinter.Text(self.mainwin, width=6, height=1,
                                     font=("宋体", 13))  # text实际上是一个文本编辑器
        self.VoltView.place(x=120, y=260)  # 显示
        self.VoltView.insert(tkinter.INSERT, "%0.1f" % float(self.volt) + '\n')

        # 状态反馈显示框
        self.ReceDataView = tkinter.Text(self.mainwin, width=30, height=1,
                                         font=("宋体", 13))  # text实际上是一个文本编辑器
        self.ReceDataView.place(x=290, y=300)  # 显示
        self.ReceDataView.insert(tkinter.INSERT, "通讯未连接" + '\n')

    def show(self):
        self.mainwin.mainloop()

    def clean_color(self):
        # 将列表中的按钮颜色变成灰色
        buttons = [self.button_A, self.button_B, self.button_C, self.button_ABC, self.button_ACB,
                   self.button_BAC, self.button_BCA, self.button_CAB, self.button_CBA]
        for button in buttons:
            button['bg'] = 'grey'

    def button_connect_click(self):
        # 点击连接按钮后的操作
        self.button_connect['bg'] = 'grey'
        self.my_serial = Communication(self.port, self.band, 0.5)  # 建立连接
        self.ReceDataView.delete("1.0", "end")
        if self.my_serial.is_open_engine():
            self.ReceDataView.insert(tkinter.INSERT, "通讯已连接" + '\n')
        self.button_connect['bg'] = 'green'

    def button_start_click(self):
        # 点击启动按钮后的操作
        self.my_serial.Send_data(bytes.fromhex(command_list["启动"]))  # 发送启动命令
        self.ReceDataView.delete("1.0", "end")
        self.ReceDataView.insert(tkinter.INSERT, "机器已启动" + '\n')
        self.button_start['bg'] = 'green'
        self.button_stop['bg'] = 'grey'

    def button_stop_click(self):
        # 点击停止按钮后的操作
        self.my_serial.Send_data(bytes.fromhex(command_list["停止"]))  # 发送停止命令
        self.ReceDataView.delete("1.0", "end")
        self.ReceDataView.insert(tkinter.INSERT, "机器已停止" + '\n')
        self.button_stop['bg'] = 'red'
        self.button_start['bg'] = 'grey'

    def button_ABC_click(self):
        # 点击ABC后的操作
        self.my_serial.Send_data(bytes.fromhex(command_list["移相ABC"]))  # 发送移相ABC的命令
        self.ReceDataView.delete("1.0", "end")
        self.ReceDataView.insert(tkinter.INSERT, "移相ABC" + '\n')
        self.clean_color()
        self.button_ABC['bg'] = 'green'

    """之后的函数格式同ABC"""

    def button_ACB_click(self):
        self.my_serial.Send_data(bytes.fromhex(command_list["移相ACB"]))
        self.ReceDataView.delete("1.0", "end")
        self.ReceDataView.insert(tkinter.INSERT, "移相ACB" + '\n')
        self.clean_color()
        self.button_ACB['bg'] = 'green'

    def button_BAC_click(self):
        self.my_serial.Send_data(bytes.fromhex(command_list["移相BAC"]))
        self.ReceDataView.delete("1.0", "end")
        self.ReceDataView.insert(tkinter.INSERT, "移相BAC" + '\n')
        self.clean_color()
        self.button_BAC['bg'] = 'green'

    def button_BCA_click(self):
        self.my_serial.Send_data(bytes.fromhex(command_list["移相BCA"]))
        self.ReceDataView.delete("1.0", "end")
        self.ReceDataView.insert(tkinter.INSERT, "移相BCA" + '\n')
        self.clean_color()
        self.button_BCA['bg'] = 'green'

    def button_CAB_click(self):
        self.my_serial.Send_data(bytes.fromhex(command_list["移相CAB"]))
        self.ReceDataView.delete("1.0", "end")
        self.ReceDataView.insert(tkinter.INSERT, "移相CAB" + '\n')
        self.clean_color()
        self.button_CAB['bg'] = 'green'

    def button_CBA_click(self):
        self.my_serial.Send_data(bytes.fromhex(command_list["移相CBA"]))
        self.ReceDataView.delete("1.0", "end")
        self.ReceDataView.insert(tkinter.INSERT, "移相CBA" + '\n')
        self.clean_color()
        self.button_CBA['bg'] = 'green'

    def button_A_click(self):
        self.my_serial.Send_data(bytes.fromhex(command_list["缺相A"]))
        self.ReceDataView.delete("1.0", "end")
        self.ReceDataView.insert(tkinter.INSERT, "缺相A" + '\n')
        self.clean_color()
        self.button_A['bg'] = 'green'

    def button_B_click(self):
        self.my_serial.Send_data(bytes.fromhex(command_list["缺相B"]))
        self.ReceDataView.delete("1.0", "end")
        self.ReceDataView.insert(tkinter.INSERT, "缺相B" + '\n')
        self.clean_color()
        self.button_B['bg'] = 'green'

    def button_C_click(self):
        self.my_serial.Send_data(bytes.fromhex(command_list["缺相C"]))
        self.ReceDataView.delete("1.0", "end")
        self.ReceDataView.insert(tkinter.INSERT, "缺相C" + '\n')
        self.clean_color()
        self.button_C['bg'] = 'green'

    def button_confirm_click(self):
        # 点击设置按钮后的操作
        self.my_serial.Send_data(bytes.fromhex(cal_command(self.freq, self.volt)))  # 发送调压调频命令
        print(cal_command(self.freq, self.volt))
        self.ReceDataView.delete("1.0", "end")
        self.ReceDataView.insert(tkinter.INSERT, "调频：{}Hz，调压：{}V".format(self.freq, round(self.volt, 1)) + '\n')

    def button_freq1_click(self):
        # 点击50按钮后的操作
        self.freq = 50  # 将频率设置为50
        self.button_freq1['bg'] = 'green'
        self.button_freq2['bg'] = 'grey'

    def button_freq2_click(self):
        # 点击60按钮后的操作
        self.freq = 60   # 将频率设置为60
        self.button_freq2['bg'] = 'green'
        self.button_freq1['bg'] = 'grey'

    def button_volt1_click(self):
        # 点击380按钮后的操作
        self.volt = 380   # 将电压设置为380
        self.VoltView.delete("1.0", "end")
        self.VoltView.insert(tkinter.INSERT, "%0.1f" % float(self.volt) + '\n')
        self.button_volt1['bg'] = 'green'
        self.button_volt2['bg'] = 'grey'

    def button_volt2_click(self):
        # 点击418按钮后的操作
        self.volt = 418  # 将电压设置为418
        self.VoltView.delete("1.0", "end")
        self.VoltView.insert(tkinter.INSERT, "%0.1f" % float(self.volt) + '\n')
        self.button_volt2['bg'] = 'green'
        self.button_volt1['bg'] = 'grey'

    def button_voltup_click(self):
        # 点击电压上键的操作
        self.volt += 0.1  # 电压加0.1
        self.VoltView.delete("1.0", "end")
        self.VoltView.insert(tkinter.INSERT, "%0.1f" % float(self.volt) + '\n')  # 更新电压显示栏

    def button_voltdown_click(self):
        self.volt -= 0.1  # 电压减0.1
        self.VoltView.delete("1.0", "end")
        self.VoltView.insert(tkinter.INSERT, "%0.1f" % float(self.volt) + '\n')  # 更新电压显示栏


if __name__ == '__main__':
    # my_ser1 = MainSerial()
    # my_ser1.show()
    print(cal_command(60,460))
    print(cal_command(50,460))

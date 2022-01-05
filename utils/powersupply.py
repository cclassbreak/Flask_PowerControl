from math import sqrt
import time
from typing import Tuple
import serial
from configparser import ConfigParser
import logging

class PowerSupply():
    _instance = None
    COMMAND = {"STOP": '7B0008010F00187D',
        "START": '7B0008010FFF177D',
        "ABC": '7B0009015A4000A47D',
        "ACB": '7B0009015A4001A57D',
        "BAC": '7B0009015A4002A67D',
        "BCA": '7B0009015A4003A77D',
        "CAB": '7B0009015A4004A87D',
        "CBA": '7B0009015A4005A97D',
        "SFC-A": '7B0009015A4006AA7D',
        "SFC-B": '7B0009015A4007AB7D',
        "SFC-C": '7B0009015A4008AC7D',
        'CHECK_POWER': '7B000801F0AFA87D',
        'CHECK_MODE': '7B000801A540EE7D'
        }
    MODE_FEEDBACK = {0: 'ABC',
        1: 'ACB',
        2: 'BAC',
        3: 'BCA',
        4: 'CAB',
        5: 'CBA',
        6: 'SFC-A',
        7: 'SFC-B',
        8: 'SFC-C',
        9: '未启动' # For APC only. Ainuo ON/OFF need to be checked by its voltage
    }

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self) -> None:
        config = ConfigParser()
        config.read('config.ini')
        self.MODEL = config.get('PowerSupply', 'MODEL')
        if self.MODEL not in ['APC', 'Ainuo']:
            logging.error(f'Model error: {self.MODEL}')
            raise ValueError('Power supply model not recognize!')
        self.COM_PORT = config.get('PowerSupply', 'COM_PORT')
        self.serial = serial.Serial(self.COM_PORT, 38400, timeout=1)
        self.mode = None
        self.voltage = None
        self.frequency = None
        self.in_use = None

    def set_mode(self, mode=None):
        '''
        START, STOP, ABC, ACB, BAC, BCA, CAB, CBA, SFC-A, SFC-B, SFC-C
        '''
        if mode == self.mode:
            return
        mode = mode.upper()
        if mode not in PowerSupply.COMMAND:
            logging.error(f'Mode code not recognize: {mode} ')
            raise ValueError(mode)
        if self.in_use==False and mode != 'STOP':
            self.serial.write(bytes.fromhex(PowerSupply.COMMAND['START']))
            time.sleep(.2)
        self.serial.write(bytes.fromhex(PowerSupply.COMMAND[mode]))
        self.mode = mode
        if mode == "STOP":
            self.in_use = False
        else:
            self.in_use = True
            
    def set_power(self, volt=None, freq=None):
        """
        计算方法 频率*100，再转换为16进制，得到一个四位数，对应命令中的两个数据为
        线电压*10，除以根号3得到相电压，再转换为16进制，也得到一个四位数，对应命令中的两个数据位
        """
        if volt == self.voltage and freq ==self.frequency:
            return
        self.voltage = volt
        self.frequency = freq
        freq = int(freq * 100)  # 频率*100
        volt = int(volt * 10 / sqrt(3))  # 电压*100/根号3
        freq = hex(freq)  # 将10进制数转换为16进制
        freq = freq.replace("0x", "")  # hex得到的16进制前缀为0x，需要去掉
        value = hex(volt)  # 将10进制数转换为16进制
        value = value.replace("0x", "")  # hex得到的16进制前缀为0x，需要去掉
        value = value.rjust(4, '0')  # 转换得到的16进制数前面补0得到一个四位数
        freq = freq.rjust(4, '0')  # 转换得到的16进制数前面补0得到一个四位数
        freq1 = freq[0:2]  # 四位数的前两位对应一个数据位
        freq2 = freq[2:4]  # 四位数的后两位对应一个数据位
        value1 = value[0:2]  # 四位数的前两位对应一个数据位
        value2 = value[2:4]  # 四位数的后两位对应一个数据位
        str1 = "00 0E 01 5A 50 00 00 {} {} {} {}".format(value1, value2, freq1, freq2)
        str1 = str1.upper()    # 转换为大写
        packet = bytes.fromhex(str1)  # 将十六进制转化为二进制
        check = self._uchar_checksum(packet, byteorder='little')  # 计算校验和
        check = hex(check)  # 将校验和转化为十六进制
        check = check.replace("0x", "")  # 去掉0x前缀
        check.rjust(2, '0')  # 转换得到的16进制数前面补0得到一个二位数
        check = check.upper() # 转化为大写
        command = "7B" + " " + str1 + " " + check + " " + "7D"  # 加上首部，尾部
        command = command.replace(' ','')
        self.serial.write(bytes.fromhex(command))
    
    def get_mode(self) -> str:
        self.serial.reset_output_buffer()
        self.serial.reset_input_buffer()
        self.serial.write(bytes.fromhex(PowerSupply.COMMAND['CHECK_MODE']))
        feedback = self.serial.read_until(b'}')
        try:
            code = int(feedback[6])
            feedback_mode = PowerSupply.MODE_FEEDBACK[code]
        except Exception as e:
            logging.error(e)
            logging.error(f'Mode feedback error:{feedback.hex()}')
            feedback_mode = 'Err'
        if self.MODEL=='Ainuo':
            time.sleep(.2)
            voltage,_ = self.get_power()
            feedback_mode = '未启动' if float(voltage) < 1 else feedback_mode
        return feedback_mode
    
    def get_power(self) -> Tuple: 
        '''
        return a tuple of (voltage: float, frequency: float)
        '''
        self.serial.reset_output_buffer()
        self.serial.reset_input_buffer()
        self.serial.write(bytes.fromhex(PowerSupply.COMMAND['CHECK_POWER']))
        feedback = self.serial.read_until(b'}')
        try:
            vol_u_hex = feedback[7:9].hex()
            fre_u_hex = feedback[11:13].hex()
            vol_u = int(vol_u_hex,16)*0.1
            fre_u = int(fre_u_hex,16)*0.01
            vol_v_hex = feedback[25:27].hex()
            vol_v = int(vol_v_hex,16)*0.1
            if vol_u<1:
                vol_xian = vol_v*1.732
            else:
                vol_xian = vol_u*1.732
            vol_output = format(vol_xian, '0.1f')
        except Exception as e:
            logging.error(e)
            logging.error(f'power setting feedback error:{feedback}')
            vol_output, fre_u = 'Err', 'Err'
        return (vol_output, fre_u)     

    def close_serial(self):
        self.serial.close()


    def _uchar_checksum(self, data, byteorder='little'):
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


if __name__ == '__main__':
    power_supplier = PowerSupply()
    # power_supplier.set_mode(mode='STOP')
    # time.sleep(.4)
    # power_supplier.set_mode(mode='ABC')
    # time.sleep(.4)
    power_supplier.set_power(volt=460, freq=50)
    # time.sleep(.4)
    # power_supplier.get_mode()
    # time.sleep(.4)
    # power_supplier.get_power()
# -*- coding: utf-8 -*-

import serial
import UI_IP_Phone_Tester

MAX_WAIT_BYTES = 200    #максимальное количество байт в буфере порта на прием
NUMBER_SCAN_PORTS = 5  #количество портов для сканирования

class RS_IP_Phone_Tester(object):


    def scan_COM_ports(self):
        """scan for available ports. return a list of tuples (num, name)"""
        # перечень доступных портов
        available = []
        for i in range(NUMBER_SCAN_PORTS):
            try:
                s = serial.Serial(i)
                available.append((s.portstr))
                s.close()   # explicit close 'cause of delayed GC in java
            except serial.SerialException:
                pass
        return available


    def Init_RS_Var(self, baudrate):
        '''
        Первичная инициализация переменных для RS
        :param baudrate:
        :return None:
        '''
        # период опроса порта
        if baudrate == 115200:
            self.time_to_rx = 100#
        elif baudrate == 57600:
            self.time_to_rx = 100#
        elif baudrate == 38400:
            self.time_to_rx = 100#
        elif baudrate == 19200:
            self.time_to_rx = 200#
        elif baudrate == 9600:
            self.time_to_rx = 200#
        elif baudrate == 1200:
            self.time_to_rx = 400#
        #начальные данные для передатчика
        self.RX_Data = bytearray()


    def Serial_Config(self, baudrate, nom_com):
        '''#*********************************************************************
        # настройка порта nom_com на скорость baudrate
        # {int} [baudrate] - скорость работы порта
        # {str} [nom_com] - номер ком порта
        #*********************************************************************'''
        self.ser = serial.Serial(nom_com,#'COM25',
                    baudrate=baudrate,#9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=0,
                    bytesize=serial.EIGHTBITS,
                    xonxoff=0)


    def Serial_Close(self):
        '''
        #*********************************************************************
        # закрыть порт
        #*********************************************************************
        :return:
        '''
        if self.ser.isOpen():
            self.ser.close()

    @property
    def Check_Serial(self):
        '''
        проверка открыт ли порт
        :return: True/ False
        '''
        if self.ser.isOpen():
            return True
        else:
            return False


    def Recieve_RS_Data(self):
        '''
        #*********************************************************************
        # проверка наличия данных в буфере RS
        #*********************************************************************
        :return: Полученные данные
        '''
        self.RX_Data = bytearray()  #данных нет
        while self.ser.inWaiting() > 0:
            self.RX_Data = self.ser.read(MAX_WAIT_BYTES)
        return self.RX_Data


    def Send_Command(self, data, app_mode = None):
        '''
        подготовка данных для отправки
        :param data: {int list} данные для отправки
        :param app_mode: {str} 'TEST' - для тестового режима
        :return: {bytearray} отправленные данные / None если не отправлено
        '''
        if self.ser.isOpen():
            # преобразуем данные если нужно
            if isinstance(data, bytearray):
                data_to_send = data
            else:
                data_to_send = bytearray()
                for d in data:
                    if isinstance(d, int):
                        data_to_send += d.to_bytes(1,'little')
                    else:
                        return None
            self.ser.write(data_to_send)
            if app_mode:
                self.Show_TX_DATA(data_to_send)
            return data_to_send
        else:
            return None


    def Show_RX_DATA(self):
        '''
        #*********************************************************************
        # вывести полученный пакет из self.RX_Data
        #*********************************************************************
        :return:
        '''
        print("получен пакет")
        for i in range(0,len(self.RX_Data)):
            print(i,': ', hex(self.RX_Data[i]),' ;',chr(self.RX_Data[i]))


    def Show_TX_DATA(self, data):
        '''
        #*********************************************************************
        # вывести отправленный пакет в RS
        #*********************************************************************
        :return:
        '''
        print("передан пакет")
        for i in range(0,len(data)):
            print(i,': ', hex(data[i]),' ;',chr(data[i]))

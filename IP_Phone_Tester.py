# -*- coding: utf-8 -*-
from RS_IP_Phone_Tester import *
from PyQt5.QtCore import QBasicTimer
from UI_IP_Phone_Tester import *
import sys

class IP_Phone_Tester(QtWidgets.QMainWindow, Ui_IP_Phone_Tester):

    # определяем константы
    MODE_TEST = True    # вкл. тестовый режим
    CUR_CMD = {         # возможные состояния программы
        "IDLE": 0,
        "CLEAR": 1,
        "CHECK": 2,
        "RELE": 3,
    }
    BAUDRATES = ['1200', '9600', '19200', '38400', '57600', '115200']  # возможные значения скоростей для RS-232
    LENGTH_LED_CMD = 8      # длина принимаемого пакета
    READ_BYTES = 100        # количество байт для чтения
    MAX_WAIT_BYTES = 200    # максимальное количество байт в буфере порта на прием
    NUMBER_SCAN_PORTS = 20  # количество портов для сканирования
    START = 0x40
    STOP = 0x5E
    SEPARATOR = 0x7C
    CMD_MIC = {
        'IDLE':             bytearray([0x40,0x30,0x7C,0x7C,0x5E]),
        'REQ_DIALTONE':     bytearray([0x40,0x34,0x7C,0x7C,0x5E]),
        'LED1_ON':          bytearray([0x40,0x35,0x7C,0x31,0x7C,0x31,0x5E]),
        'LED2_ON':          bytearray([0x40,0x35,0x7C,0x31,0x7C,0x32,0x5E]),
        'LED1_BLINK':       bytearray([0x40,0x35,0x7C,0x32,0x7C,0x31,0x5E]),
        'LED2_BLINK':       bytearray([0x40,0x35,0x7C,0x32,0x7C,0x32,0x5E]),
        'LED1_OFF':         bytearray([0x40,0x35,0x7C,0x30,0x7C,0x31,0x5E]),
        'LED2_OFF':         bytearray([0x40,0x35,0x7C,0x30,0x7C,0x32,0x5E]),
        'LEDS_ON':          bytearray([0x40,0x36,0x7C,0x31,0x7C]), # последние 3 байта не показаны
        'LEDS_OFF':         bytearray([0x40,0x36,0x7C,0x30,0x7C]), # последние 3 байта не показаны
        'LEDS_BLINK':       bytearray([0x40,0x36,0x7C,0x32,0x7C]), # последние 3 байта не показаны
    }


    # инициализация окна
    # pyuic5 UI_IP_Phone_Tester.ui -o UI_IP_Phone_Tester.py
    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        # инициализация интерфейса
        self.setupUi(self)
        # определяем таймер
        self.timer_RX_RS = QBasicTimer()
        self.timer_RX_RS.stop()
        # подключаем модули
        self.rs = RS_IP_Phone_Tester()  # подключение функций работы по RS
        # инициализация переменных
        self.Init_Var()
        # настройка действий по кнопкам
        # self.Init_Widgets()
        self.test()
        pass


    def test(self):
        for key, val in self.CMD_MIC.items():
            print(key)
            print(val)


    def Init_Var(self):
        self.__Status_new = self.CUR_CMD["IDLE"] #текущее состояние

    def Init_Widget(self):
        pass

    @property
    def status_new(self):
        '''
        # установка нового значения свойства status_new
        '''
        return self.__Status_new

    @status_new.setter
    def status_new(self, status):
        '''
        # установка нового значения свойства status_new
        '''
        self.__Status_new = status


    def Parsing_Rx_Pack(self, data_in):
        """
        парсинг полученного пакета
        param: data_in: {bytes}
        return: [keys, status, u_pow, u_ampl, i_ampl, err]:
        """
        keys = status = u_pow = u_ampl = i_ampl = 0
        if len(data_in) != self.LENGTH:
            err = True
        else:
            err = False
            # выделяем данные из пакета
            keys = int.from_bytes(data_in[KEYS_POS: KEYS_POS+1], byteorder='little') #преобразуем в int
            status = int.from_bytes(data_in[STATUS_POS:STATUS_POS+1], byteorder='little') #преобразуем в int
            u_pow = int.from_bytes(data_in[U_POW_POS:U_POW_POS+1], byteorder='little') #преобразуем в int
            u_ampl = int.from_bytes(data_in[U_AMPL_POS:U_AMPL_POS+1], byteorder='little') #преобразуем в int
            i_ampl = int.from_bytes(data_in[I_AMPL_LO_POS:I_AMPL_HI_POS+1], byteorder='little') #преобразуем в int
        return (keys, status, u_pow, u_ampl, i_ampl, err)


    def analyze_pack(self):
        '''
        #*********************************************************************
        # анализ принятых данных из RS
        #*********************************************************************
        :return:
        '''
        #проверка на стартовую и стоповую посылку
        if self.rs_receive_pack[:1] == self.START and self.rs_receive_pack[:-1] == self.STOP:
            # показать принятые данные в тестовом режиме
            if self.MODE_TEST:
                self.rs.Show_RX_DATA()
            # производим разбор принятого пакета
            cmd_rx, self.num_chnl, param, hours, minutes, seconds, stat_rele_1, stat_rele_2, err = self.app.Parsing_Rx_Pack(self.rs_receive_pack)
            # проверка была ли ошибка длины в принятых данных
            if err == True:
                return ['Error']
            if cmd_rx == CUR_CMD["CLEAR"] and self.status_new == CUR_CMD["CLEAR"]:
                if param == 1:
                    self.app.Set_Frame_Color('grey', self.num_chnl)
                    self.app.Set_Label_Text( 'нет питания', self.num_chnl)
                    return 'Ok'
            elif cmd_rx == CUR_CMD["CHECK"] and self.status_new == CUR_CMD["CHECK"]:
                if param == 0:
                    self.app.Set_Frame_Color('red', self.num_chnl)
                    self.app.Set_Label_Text( 'выключен', self.num_chnl )
                elif param == 1:
                    self.app.Set_Frame_Color('green', self.num_chnl)
                    self.app.Set_Label_Text('t=%dч:%dмин:%2dс' % (hours, minutes, seconds) , self.num_chnl )
                elif param == 2:
                    self.app.Set_Frame_Color('grey', self.num_chnl)
                    self.app.Set_Label_Text('t=%dч:%dмин:%2dс' % (hours, minutes, seconds) , self.num_chnl )
                if stat_rele_1 == 1:
                    self.app.Set_Frame_Color('green', 21)
                    self.app.Set_Label_Text('включено', 21)
                else:
                    self.app.Set_Frame_Color('red', 21)
                    self.app.Set_Label_Text('выключено', 21)
                if stat_rele_2 == 1:
                    self.app.Set_Frame_Color('green', 22)
                    self.app.Set_Label_Text('включено', 22)
                else:
                    self.app.Set_Frame_Color('red', 22)
                    self.app.Set_Label_Text('выключено', 22)
                return 'Ok'
            elif cmd_rx == CUR_CMD["RELE"] and self.status_new == CUR_CMD["RELE"]:
                if self.num_chnl != 0:
                    # ответ получен, сообщить что все установлено нормально
                    text = "Настройки параметров "+str(self.num_chnl)+" реле успешно записаны."
                    QtWidgets.QMessageBox.warning(self, 'Сообщение', text, QtWidgets.QMessageBox.Ok)
                else:
                    QtWidgets.QMessageBox.warning(self, 'Сообщение', "Режим заряда выключен", QtWidgets.QMessageBox.Ok)
                self.Set_Status_AKB(CUR_CMD["IDLE"])
                return 'Ok'
            else:
                #иначе возвращаем Error
                return 'Error'
        else:
            return 'Error'


    def timerEvent(self, e):
        '''
        #*********************************************************************
        # обработка событий по таймеру
        #*********************************************************************
        :param e:
        :return:
        '''
        self.timer_RX_RS.stop() #выключаем таймер
        self.rs_receive_pack = self.rs.Recieve_RS_Data()    #получаем аднные
        #есть ли принятые данные
        if self.rs_receive_pack != '' and self.status_new != CUR_CMD["IDLE"]:
            # анализируем полученные данные
            self.result_analyze = self.analyze_pack()
            #данные есть, проверяем что с ними нужно сделать
            if self.result_analyze == 'Ok':
                if self.status_new == CUR_CMD["CLEAR"]:
                    #ничего не делаем в состоянии IDLE
                    self.Set_Status_AKB(CUR_CMD["IDLE"])
                if self.status_new == CUR_CMD["CHECK"]:
                    # продолжаем опрос следующего канала
                    if self.num_chnl < 20:
                        self.num_chnl += 1
                    else:
                        self.num_chnl = 1
                    # отправить "опрос каналов"
                    self.rs.Send_Command_AKB(CUR_CMD['CHECK'], self.num_chnl)
                    # запускаем таймер ожидания ответа 1 c
                    self.timer_RX_RS.start(400, self)
            else:
                #ответ не получен
                QtWidgets.QMessageBox.warning(self, 'Ошибка',"Нет ответа от модуля.", QtWidgets.QMessageBox.Ok)
        #принятых данных нет
        elif self.status_new == CUR_CMD["IDLE"]:
            return
        else:
            if self.status_new == CUR_CMD["CHECK"]:
                # вернутся к исходному виду кнопок
                self.event.pb_Stop_Polling_Header()
            #ответ не получен
            QtWidgets.QMessageBox.warning(self, 'Ошибка',"Нет ответа от модуля.", QtWidgets.QMessageBox.Ok)
            #переходим в IDLE
            self.Set_Status_AKB(CUR_CMD["IDLE"])
        return

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = IP_Phone_Tester()
    myapp.show()
    sys.exit(app.exec_())

# -*- coding: utf-8 -*-
from RS_IP_Phone_Tester import *
from PyQt5.QtCore import QBasicTimer
from UI_IP_Phone_Tester import *
import sys

class IP_Phone_Tester(QtWidgets.QMainWindow, Ui_IP_Phone_Tester):

    # определяем константы
    MODE_TEST = False    # вкл. тестовый режим
    CUR_CMD = {         # возможные состояния программы
        "NONE": 0,
        "IDLE": 1,
    }
    BAUDRATES = ['1200', '9600', '19200', '38400', '57600', '115200']  # возможные значения скоростей для RS-232
    LENGTH_LED_CMD = 8      # длина принимаемого пакета
    READ_BYTES = 100        # количество байт для чтения
    MAX_WAIT_BYTES = 200    # максимальное количество байт в буфере порта на прием
    NUMBER_SCAN_PORTS = 20  # количество портов для сканирования
    START = 0x40
    STOP = 0x5E
    SEPARATOR = 0x7C
    CMD_TX = {
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
        'HENDSET_ON':       bytearray([0x40,0x37,0x7C,0x31,0x7C,0x5E]),
        'HENDSET_OFF':      bytearray([0x40,0x37,0x7C,0x30,0x7C,0x5E]),
        'MIC_ON':           bytearray([0x40,0x38,0x7C,0x31,0x7C,0x5E]),
        'MIC_OFF':          bytearray([0x40,0x38,0x7C,0x30,0x7C,0x5E]),
        'SPEAK_ON':         bytearray([0x40,0x39,0x7C,0x31,0x7C,0x5E]),
        'SPEAK_OFF':        bytearray([0x40,0x39,0x7C,0x30,0x7C,0x5E]),
        'HORN_ON':          bytearray([0x40,0x31,0x30,0x7C,0x31,0x7C,0x5E]),
        'HORN_OFF':         bytearray([0x40,0x31,0x30,0x7C,0x30,0x7C,0x5E]),
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
        self.Init_Widgets()
        pass

    def test(self):
        for i in 'hallo world':
            if i == 'a':
                break
            else:
                print('есть')
        else:
            print('Буквы a в строке нет')

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


    def Init_Var(self):
        self.__Status_new = self.CUR_CMD["NONE"] #текущее состояние
        self.cb_State = []
        self.rs_receive_pack = bytearray()
        for i in range (1,31):
            self.cb_State.append(False)


    def Init_Widgets(self):
        #настройка списка для выбора порта
        self.comboBox_COM.addItems(self.rs.scan_COM_ports())
        self.comboBox_COM.setCurrentIndex(0)
        #добавляем нужные скорости в comboBox_Baudrate
        self.comboBox_Baudrate.addItems(self.BAUDRATES)
        self.comboBox_Baudrate.setCurrentIndex(4)        #добавляем нужные скорости в comboBox_Baudrate
        # обработчики для кнопок
        self.pushButton_open_COM.clicked.connect(self.pb_Open_COM_Header)
        self.pushButton_close_COM.clicked.connect(self.pb_Close_COM_Header)
        self.pushButton_Check_Connect.clicked.connect(self.pb_Check_Connect_Header)
        self.pushButton_LED_1.clicked.connect(self.pb_LED1_Header)
        self.pushButton_LED_2.clicked.connect(self.pb_LED2_Header)
        self.pushButton_Hendset.clicked.connect(self.pb_Hendset_Header)
        self.pushButton_Mic.clicked.connect(self.pb_Mic_Header)
        self.pushButton_Speak.clicked.connect(self.pb_Speak_Header)
        self.pushButton_Horn.clicked.connect(self.pb_Horn_Header)
        for i in range(1,31):
            eval('self.checkBox_%i.stateChanged.connect(self.cb_Header)'%i)


    def pb_Open_COM_Header(self):
        '''
        :return:
        '''
        self.status_new = self.CUR_CMD["IDLE"]
        self.comboBox_COM.setDisabled(1)
        self.comboBox_Baudrate.setDisabled(1)
        baudrate = int(self.comboBox_Baudrate.currentText())
        nom_com_port = self.comboBox_COM.currentText()
        # конфигурируем RS
        self.rs.Serial_Config(baudrate, nom_com_port)
        self.rs.Init_RS_Var(baudrate)
        # изменяем видимость кнопок
        self.Enable_Widgets()
        self.timer_RX_RS.start(self.rs.time_to_rx, self) #отправляем запрос защитного кода через self.time_to_rx мс


    def pb_Close_COM_Header(self):
        '''
        #*********************************************************************
        # активация кнопок после выбора порта и скорости
        #*********************************************************************
        :return:
        '''
        self.rs.Recieve_RS_Data()
        # закрываем порт
        if self.rs.Check_Serial:
            self.rs.Serial_Close()
        # изменяем видимость кнопок
        self.Disable_Widgets()
        self.status_new = self.CUR_CMD['NONE']


    def pb_Check_Connect_Header(self):
        self.rs.Send_Command(self.CMD_TX['REQ_DIALTONE'], self.MODE_TEST)

    def pb_LED1_Header(self, d):
        if self.pushButton_LED_1.isChecked():
            # кнопка нажата
            if self.radioButton_Perm.isChecked():
                self.rs.Send_Command(self.CMD_TX['LED1_ON'], self.MODE_TEST)
            else:
                self.rs.Send_Command(self.CMD_TX['LED1_BLINK'], self.MODE_TEST)
        else:
            # кнопка отжата
            self.rs.Send_Command(self.CMD_TX['LED1_OFF'], self.MODE_TEST)

    def pb_LED2_Header(self):
        if self.pushButton_LED_2.isChecked():
            # кнопка нажата
            if self.radioButton_Perm.isChecked():
                self.rs.Send_Command(self.CMD_TX['LED2_ON'], self.MODE_TEST)
            else:
                self.rs.Send_Command(self.CMD_TX['LED2_BLINK'], self.MODE_TEST)
        else:
            # кнопка отжата
            self.rs.Send_Command(self.CMD_TX['LED2_OFF'], self.MODE_TEST)

    def pb_Hendset_Header(self):
        if self.pushButton_Hendset.isChecked():
            # кнопка нажата
            self.rs.Send_Command(self.CMD_TX['HENDSET_ON'], self.MODE_TEST)
        else:
            # кнопка отжата
            self.rs.Send_Command(self.CMD_TX['HENDSET_OFF'], self.MODE_TEST)

    def pb_Mic_Header(self):
        if self.pushButton_Mic.isChecked():
            # кнопка нажата
            self.rs.Send_Command(self.CMD_TX['MIC_ON'], self.MODE_TEST)
        else:
            # кнопка отжата
            self.rs.Send_Command(self.CMD_TX['MIC_OFF'], self.MODE_TEST)

    def pb_Speak_Header(self):
        if self.pushButton_Speak.isChecked():
            # кнопка нажата
            self.rs.Send_Command(self.CMD_TX['SPEAK_ON'], self.MODE_TEST)
        else:
            # кнопка отжата
            self.rs.Send_Command(self.CMD_TX['SPEAK_OFF'], self.MODE_TEST)

    def pb_Horn_Header(self):
        if self.pushButton_Horn.isChecked():
            # кнопка нажата
            self.rs.Send_Command(self.CMD_TX['HORN_ON'], self.MODE_TEST)
        else:
            # кнопка отжата
            self.rs.Send_Command(self.CMD_TX['HORN_OFF'], self.MODE_TEST)

    def cb_Header(self):
        for i in range (1,31):
            state = eval('self.checkBox_%i.isChecked()'%i)
            data = bytearray()
            if state == True and self.cb_State[i-1] == False:
                self.cb_State[i-1] = True
                if self.radioButton_Perm.isChecked():
                    data += self.CMD_TX['LEDS_ON']
                else:
                    data += self.CMD_TX['LEDS_BLINK']
                num_str = str(i)
                if i < 10:
                    num_str = '0' + num_str
                # добавляем номер светодиода
                data += ord(num_str[0]).to_bytes(1, 'little')
                data += ord(num_str[1]).to_bytes(1, 'little')
                data += self.STOP.to_bytes(1, 'little')
                # отправляем команду
                self.rs.Send_Command(data, self.MODE_TEST)
            elif state == False and self.cb_State[i - 1] == True:
                self.cb_State[i-1] = False
                data += self.CMD_TX['LEDS_OFF']
                num_str = str(i)
                if i < 10:
                    num_str = '0' + num_str
                # добавляем номер светодиода
                data += ord(num_str[0]).to_bytes(1, 'little')
                data += ord(num_str[1]).to_bytes(1, 'little')
                data += self.STOP.to_bytes(1, 'little')
                # отправляем команду
                self.rs.Send_Command(data, self.MODE_TEST)
        return True


    def Enable_Widgets(self):
        self.comboBox_COM.setDisabled(1)
        self.comboBox_Baudrate.setDisabled(1)
        self.pushButton_open_COM.setDisabled(1)
        self.pushButton_close_COM.setEnabled(1)
        self.radioButton_Perm.setEnabled(1)
        self.radioButton_Perm.setChecked(1)
        self.radioButton_Blink.setEnabled(1)
        self.pushButton_Next_LED.setEnabled(1)
        self.pushButton_LED_1.setEnabled(1)
        self.pushButton_LED_2.setEnabled(1)
        self.pushButton_Hendset.setEnabled(1)
        self.pushButton_Mic.setEnabled(1)
        self.pushButton_Speak.setEnabled(1)
        self.pushButton_Horn.setEnabled(1)
        self.pushButton_Check_Connect.setEnabled(1)
        for i in range(1,31):
            eval('self.checkBox_%i.setEnabled(1)'%i)

    def Disable_Widgets(self):
        self.comboBox_COM.setEnabled(1)
        self.comboBox_Baudrate.setEnabled(1)
        self.pushButton_open_COM.setEnabled(1)
        self.pushButton_close_COM.setDisabled(1)
        self.radioButton_Perm.setDisabled(1)
        self.radioButton_Blink.setDisabled(1)
        self.pushButton_Next_LED.setDisabled(1)
        self.pushButton_LED_1.setDisabled(1)
        self.pushButton_LED_2.setDisabled(1)
        self.pushButton_Hendset.setDisabled(1)
        self.pushButton_Mic.setDisabled(1)
        self.pushButton_Speak.setDisabled(1)
        self.pushButton_Horn.setDisabled(1)
        self.pushButton_Check_Connect.setDisabled(1)
        for i in range(1,31):
            eval('self.checkBox_%i.setDisabled(1)' % i)
            eval('self.checkBox_%i.setChecked(0)' % i)


    def Extract_Command(self, data_in):
        """
        парсинг полученного пакета
        """
        num = 0
        start_ok = False
        data = bytearray()
        # обрезаем начало до стартового символа
        for d in data_in:
            if d == self.START:
                break
            else:
                num += 1
        if num == len(data_in):
            # в принятых данных нет стартового байта, возвращаем исходный пакет
            return(data, data_in)
        else:
            tail = num
            # выделяем команду и остаток
            for d in data_in[num:]:
                tail += 1
                if d == self.START and start_ok == False:
                    data += d.to_bytes(1, 'little')
                    start_ok = True
                elif d == self.STOP and start_ok == True:
                    data += d.to_bytes(1, 'little')
                    start_ok = False
                    return(data, data_in[tail:])
                elif start_ok == True:
                    data += d.to_bytes(1, 'little')

    def Parsing_RX_Data(self, data):
        '''
        Парсинг принятых данных в data и изменение внешнего вида окна
        :param data:
        :return: True/ False
        '''
        pass #40 36 7С 3y 7C 3х1 3х2 5E,
        if len(data) > 1:
            if data[0] == self.START and data[-1:] == bytearray([self.STOP]):
                if data[1] == 0x33 and data[2] == 0x7C and data[4] == 0x7C:
                    try:
                        num = int(chr(data[5]) + chr(data[6]))
                    except ValueError:
                        return False
                    if data[3] == 0x30: # кнопка отжата
                        text = 'отжата'
                        text_for_command = 'self.frame_%i.setStyleSheet("background-color: rgb(255, 117, 53);")'
                        eval('self.label_t%i.setText("%s")' % (num, text))
                        eval(text_for_command % num)
                        return True
                    elif data[3] == 0x31: # кнопка нажата
                        text = 'нажата'
                        text_for_command = 'self.frame_%i.setStyleSheet("background-color: rgb(0, 150, 53);")'
                        eval('self.label_t%i.setText("%s")' % (num, text))
                        eval(text_for_command % num)
                        return True
        return False

    def analyze_pack(self):
        '''
        #*********************************************************************
        # анализ принятых данных из RS
        #*********************************************************************
        :return:
        '''
        # проверка на стартовую и стоповую посылку

        # показать принятые данные в тестовом режиме
        if self.MODE_TEST:
            self.rs.Show_RX_DATA()
            self.rs_receive_pack = bytearray([0x40, 0x33, 0x7C, 0x31, 0x7C, 0x33, 0x30, 0x5E])
        # производим разбор принятого пакета
        data, self.rs_receive_pack = self.Extract_Command(self.rs_receive_pack)
        res = self.Parsing_RX_Data(data)
        # проверка была ли ошибка длины в принятых данных
        if res:
            return True
        else:
            return False


    def timerEvent(self, e):
        '''
        #*********************************************************************
        # обработка событий по таймеру
        #*********************************************************************
        :param e:
        :return:
        '''
        self.timer_RX_RS.stop() #выключаем таймер
        if self.status_new != self.CUR_CMD['NONE']:
            self.rs_receive_pack += self.rs.Recieve_RS_Data()    #получаем аднные
            #есть ли принятые данные
            if self.rs_receive_pack != bytearray():
                # анализируем полученные данные
                if not self.analyze_pack():
                    QtWidgets.QMessageBox.warning(self, 'Ошибка', "Ошибка приема", QtWidgets.QMessageBox.Ok)
            self.timer_RX_RS.start(self.rs.time_to_rx, self)
        return

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = IP_Phone_Tester()
    myapp.show()
    sys.exit(app.exec_())

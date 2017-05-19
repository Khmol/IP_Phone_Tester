#coding: utf8
from RS_IP_Phone_Tester import *
# from Application_Tester_AKB import *
# from Form_Events_Tester_AKB import *
from PyQt5.QtCore import QBasicTimer
from UI_IP_Phone_Tester import *
import sys

class IP_Phone_Tester(QtWidgets.QMainWindow, Ui_IP_Phone_Tester):
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
        self.rs = RS_IP_Phone_Tester()                # подключение функций работы по RS
        # self.event = Form_Events_Tester_AKB(self)   # определение обработчиков событий
        # self.app = Application(self)

        # настройка действий по кнопкам
        # self.event.Init_Widgets()


    def Init_Var(self):
        # словарь для ID1
        self.cur_cmd = {
            "IDLE" : 0,
            "CLEAR" : 1,
            "CHECK" : 2,
            "RELE" : 3,
            }
        self.status_new = self.cur_cmd["IDLE"] #текущее состояние
        self.status_old = self.cur_cmd["IDLE"] #текущее состояние
        self.BAUDRATES = ['1200', '9600', '19200', '38400', '57600', '115200']    #возможные значения скоростей для RS-232
        self.READ_BYTES = 100    #количество байт для чтения
        self.OK_ANSWER = bytearray('OK'.encode('latin-1')) #OK
        self.MAX_WAIT_BYTES = 200    #максимальное количество байт в буфере порта на прием
        self.NUMBER_SCAN_PORTS = 20  #количество портов для сканирования
        self.SET = 1                #значения для парсинга пакета


    def Set_Status_AKB(self, new_status):
        '''
        # установка нового значения переменным STATUS
        :param new_status:
        :return:
        '''
        self.status_old = self.status_new
        self.status_new = new_status


    def analyze_pack(self):
        '''
        #*********************************************************************
        # анализ принятых данных из RS
        #*********************************************************************
        :return:
        '''
        #проверка на стартовую посылку
        if self.rs_receive_pack[:1] == self.rs.rs_start:
            #показать принятые данные
            if self.MODE == 'TEST':
                self.event.Show_RX_DATA()
            #производим рассчет CRC16 для self.rs_send_pack без последних двух байт
            cmd_rx, self.num_chnl, param, hours, minutes, seconds, stat_rele_1, stat_rele_2, err = self.app.Parsing_Rx_Pack(self.rs_receive_pack)
            # проверка была ли ошибка длины в принятых данных
            if err == True:
                return ['Error']
            if cmd_rx == self.cur_cmd["CLEAR"] and self.status_new == self.cur_cmd["CLEAR"]:
                if param == 1:
                    self.app.Set_Frame_Color('grey', self.num_chnl)
                    self.app.Set_Label_Text( 'нет питания', self.num_chnl)
                    return 'Ok'
            elif cmd_rx == self.cur_cmd["CHECK"] and self.status_new == self.cur_cmd["CHECK"]:
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
            elif cmd_rx == self.cur_cmd["RELE"] and self.status_new == self.cur_cmd["RELE"]:
                if self.num_chnl != 0:
                    # ответ получен, сообщить что все установлено нормально
                    text = "Настройки параметров "+str(self.num_chnl)+" реле успешно записаны."
                    QtWidgets.QMessageBox.warning(self, 'Сообщение', text, QtWidgets.QMessageBox.Ok)
                else:
                    QtWidgets.QMessageBox.warning(self, 'Сообщение', "Режим заряда выключен", QtWidgets.QMessageBox.Ok)
                self.Set_Status_AKB(self.cur_cmd["IDLE"])
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
        if self.rs_receive_pack != '' and self.status_new != self.cur_cmd["IDLE"]:
            # анализируем полученные данные
            self.result_analyze = self.analyze_pack()
            #данные есть, проверяем что с ними нужно сделать
            if self.result_analyze == 'Ok':
                if self.status_new == self.cur_cmd["CLEAR"]:
                    #ничего не делаем в состоянии IDLE
                    self.Set_Status_AKB(self.cur_cmd["IDLE"])
                if self.status_new == self.cur_cmd["CHECK"]:
                    # продолжаем опрос следующего канала
                    if self.num_chnl < 20:
                        self.num_chnl += 1
                    else:
                        self.num_chnl = 1
                    # отправить "опрос каналов"
                    self.rs.Send_Command_AKB(self.cur_cmd['CHECK'], self.num_chnl)
                    # запускаем таймер ожидания ответа 1 c
                    self.timer_RX_RS.start(400, self)
            else:
                #ответ не получен
                QtWidgets.QMessageBox.warning(self, 'Ошибка',"Нет ответа от модуля.", QtWidgets.QMessageBox.Ok)
        #принятых данных нет
        elif self.status_new == self.cur_cmd["IDLE"]:
            return
        else:
            if self.status_new == self.cur_cmd["CHECK"]:
                # вернутся к исходному виду кнопок
                self.event.pb_Stop_Polling_Header()
            #ответ не получен
            QtWidgets.QMessageBox.warning(self, 'Ошибка',"Нет ответа от модуля.", QtWidgets.QMessageBox.Ok)
            #переходим в IDLE
            self.Set_Status_AKB(self.cur_cmd["IDLE"])
        return

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = IP_Phone_Tester()
    myapp.show()
    sys.exit(app.exec_())

# -*- encoding: utf-8 -*-

import unittest, sys
import IP_Phone_Tester
from PyQt5 import QtWidgets

RS_LOOP = False

class TestUM(unittest.TestCase):
    def setUp(self):
        self.widg = QtWidgets.QApplication(sys.argv)
        self.app = IP_Phone_Tester.IP_Phone_Tester()
        # self.rs_receive_pack = bytearray([0x40, 0x33, 0x7C, 0x30, 0x7C, 0x30, 0x31, 0x5E])


    def test_Extract_Command(self):
        self.rs_receive_pack = bytearray()
        data, tail = self.app.Extract_Command(self.rs_receive_pack)
        self.assertEqual(data, bytearray())
        self.assertEqual(tail, bytearray())
        self.rs_receive_pack = bytearray([0x01,0x40, 0x33, 0x7C, 0x30, 0x7C, 0x30, 0x31, 0x5E, 0x40])
        data, tail = self.app.Extract_Command(self.rs_receive_pack)
        self.assertEqual(data, self.rs_receive_pack[1:-1])
        self.assertEqual(tail, bytearray([0x40]))
        self.rs_receive_pack = bytearray([0x40, 0x33, 0x7C, 0x30, 0x7C, 0x30, 0x31, 0x5E, 0x40])
        data, tail = self.app.Extract_Command(self.rs_receive_pack)
        self.assertEqual(data, self.rs_receive_pack[:-1])
        self.assertEqual(tail, bytearray([0x40]))
        self.rs_receive_pack = bytearray([0x40, 0x33, 0x7C, 0x30, 0x7C, 0x30, 0x31, 0x5E])
        data, tail = self.app.Extract_Command(self.rs_receive_pack)
        self.assertEqual(data, self.rs_receive_pack)
        self.assertEqual(tail, bytearray())
        self.rs_receive_pack = bytearray([0x41, 0x33, 0x7C, 0x30, 0x7C, 0x30, 0x31, 0x5E])
        data, tail = self.app.Extract_Command(self.rs_receive_pack)
        self.assertEqual(tail, self.rs_receive_pack)
        self.assertEqual(data, bytearray())

    def test_Parsing_RX_Data(self):
        data_in = bytearray([0x40, 0x36, 0x7C, 0x30, 0x7C, 0x30, 0x31, 0x5E])
        res = self.app.Parsing_RX_Data(data_in)
        self.assertTrue(res)
        data_in = bytearray([0x40, 0x37, 0x7C, 0x30, 0x7C, 0x30, 0x31, 0x5E])
        res = self.app.Parsing_RX_Data(data_in)
        self.assertFalse(res)
        data_in = bytearray([0x40, 0x36, 0x7C, 0x30, 0x7C, 0x40, 0x31, 0x5E])
        res = self.app.Parsing_RX_Data(data_in)
        self.assertFalse(res)
        data_in = bytearray([0x40, 0x36, 0x7C, 0x30, 0x7C, 0x40, 0x5E])
        res = self.app.Parsing_RX_Data(data_in)
        self.assertFalse(res)
        data_in = bytearray([0x40, 0x5E])
        res = self.app.Parsing_RX_Data(data_in)
        self.assertFalse(res)
        data_in = bytearray([])
        res = self.app.Parsing_RX_Data(data_in)
        self.assertFalse(res)

    def test_Widgets(self):
        res = self.app.Init_Widgets()
        self.assertEqual(res, None)
        res = self.app.Enable_Widgets()
        self.assertEqual(res, None)
        res = self.app.Disable_Widgets()
        self.assertEqual(res, None)
        res = self.app.pb_Open_COM_Header()
        self.assertEqual(res, None)
        res = self.app.pb_Close_COM_Header()
        self.assertEqual(res, None)


    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()

################################################
# demo_ds1302.py
# (C) 2021, JarutEx (https://www.jarutex.com
################################################
from machine import Pin
import time

# setting
class DS1302:
    REG_SECOND = const(0x80)
    REG_MINUTE = const(0x82)
    REG_HOUR   = const(0x84)
    REG_DAY    = const(0x86)
    REG_MONTH  = const(0x88)
    REG_WEEKDAY= const(0x8A)
    REG_YEAR   = const(0x8C)
    REG_WP     = const(0x8E)
    REG_CTRL   = const(0x90)
    REG_RAM    = const(0xC0)
    
    def __init__(self, _sclk=12, _io=13, _ce=14):
        self.pinClk = Pin( _sclk, Pin.OUT )
        self.pinIO = Pin( _io )
        self.pinCE = Pin( _ce, Pin.OUT )
        self.pinCE.value(0) # disable
        self.pinClk.value(0)
        self.rtc = [0,0,0,0,0,0,0] # y/m/d/dw/h/mi/s

    def dec2bcd(self, n):
        return ((n // 10 * 16) + (n % 10))

    def bcd2dec(self, n):
        return ((n // 16 * 10) + (n % 16))

    def write(self, data):
        self.pinIO.init(Pin.OUT)
        for i in range(8):
            bit = (data & 0x01)
            data = (data >> 1)
            self.pinIO.value(bit)
            self.pinClk.value(1)
            self.pinClk.value(0)
        
    def read(self):
        self.pinIO.init( Pin.IN )
        byte = 0
        for i in range(8):
            bit = self.pinIO.value() & 0x01
            bit = (bit << i)
            byte = (byte | bit)
            self.pinClk.value(1)
            self.pinClk.value(0)
        return byte
            
    def set(self, reg, data):
        self.pinCE.value(1)
        self.write( reg )
        self.write( data )
        self.pinCE.value(0)
            
    def get(self, reg):
        self.pinCE.value(1)
        self.write( reg+1 )
        data = self.read()
        self.pinCE.value(0)
        return data

    def now(self):
        self.rtc[0] = self.bcd2dec(self.get(REG_YEAR))+2000
        self.rtc[1] = self.bcd2dec(self.get(REG_MONTH))
        self.rtc[2] = self.bcd2dec(self.get(REG_DAY))
        self.rtc[3] = self.bcd2dec(self.get(REG_WEEKDAY))
        self.rtc[4] = self.bcd2dec(self.get(REG_HOUR))
        self.rtc[5] = self.bcd2dec(self.get(REG_MINUTE))
        self.rtc[6] = self.bcd2dec(self.get(REG_SECOND))
        
    def adjust(self, day, month, year, dow, hour, minute, second ):
        # convert
        year = year - 2000
        year = self.dec2bcd(year)
        month = self.dec2bcd(month)
        day = self.dec2bcd(day)
        dow = self.dec2bcd(dow)
        minute = self.dec2bcd(minute)
        hour = hour & 0x1F
        hour = self.dec2bcd(hour)
        second = self.dec2bcd(second)
        # adjust
        self.set(REG_YEAR, year)
        self.set(REG_MONTH, month)
        self.set(REG_DAY, day)
        self.set(REG_WEEKDAY, dow)
        self.set(REG_HOUR, hour)
        self.set(REG_MINUTE, minute)
        self.set(REG_SECOND, second)

    def show(self):
        print("{} {}-{}-{} {}:{}:{}".format(
            self.rtc[3],
            self.rtc[0], self.rtc[1], self.rtc[2],
            self.rtc[4], self.rtc[5], self.rtc[6]
            ))        

'''
# 示例程序
# main program
rtc = DS1302()
rtc.adjust(7,7,2021, 3, 17,57,00)
while True:
    rtc.now()
    rtc.show()
    time.sleep_ms(1000)
'''

#显示 LOADING...
_L=[]
_O=[]
_A=[]
_D=[]
_I=[]
_N=[]
_G=[]
_dot=[]

from ssd1306 import SSD1306_I2C
from machine import Pin,I2C

def LOADING():
    i2c=I2C(0,scl=Pin(5),sda=Pin(4))
    oled=SSD1306_I2C(i2c)

    x=5
    while x<123:
        oled.ellipse(x,58,5,5)
        x=x+1
        oled.show()
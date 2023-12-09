import framebuf
 
 
class SSD1306():
    def __init__(self,external_vcc):
        self.width = 128
        self.height = 64
        self.external_vcc = external_vcc
        self.pages = 8
        self.init_display()
 
    def init_display(self):
        for cmd in (
            0xae,        # 熄屏
            0x20, 0x00,  # 水平寻址
            0x40,        # 显示起始行地址
            0xa1,        # 正常列扫描
            0xa8, 63,    # 复用率
            0xc8,        # 正常行扫描
            0xd3, 0x00,  #设置COM偏移量，即屏幕像上偏移的行数
            0xda, 0x12,  #使用备选引脚配置，并禁用左右反置
            0xd5, 0x80,  # 设置分频因子与振荡频率
            0xd9, 0x22 if self.external_vcc else 0xf1,
            0xdb, 0x30,  # 设置vcomh电压为0.83*Vcc
            0x81, 0xff,  # 亮度最大
            0xa4,        # 使用GDDRAM中的数据显示
            0xa6,        # 设置GDDRAM中的0对应于像素点的暗
            # 关闭电荷泵
            0x8d, 0x10 if self.external_vcc else 0x14,
            0x2e,        # 禁止滚动
            0xaf):       #开屏
            self.write_cmd(cmd)
        self.fill(0)
        self.show()
    #设置水平滚动，参数：滚动区域（滚动起始页，滚动结束页），滚动方向（默认向左，填0向右），滚动速度（0-7）  
    def h_scroll(self,start=0,end=7,d=1,speed=0): 
        self.write_cmd(0x2e)     # 关闭滚动
        self.write_cmd(0x26+d) # 向左
        self.write_cmd(0x00)
        self.write_cmd(start) # 起始页
        self.write_cmd(speed) # 滚动帧率
        self.write_cmd(end) # 结束页
        self.write_cmd(0x00)
        self.write_cmd(0xff)
        self.write_cmd(0x2f) # 开启滚动
        
    #默认开启竖直向上滚动与水平向右滚动
    def scroll(self,vScrollOn=0,vStart=0,vEnd=63,vSpeed=1,hScrollOn=1,direction=0,hSpeed=0,hScrollStartPage=0,hScrollEndPage=7,
               hScrollStartColumn=0,hScrollEndColumn=127):
        if vScrollOn:
            self.write_cmd(0x2e)# 关闭滚动
            self.write_cmd(0xa3)#设置竖直滚动命令
            self.write_cmd(vStart)#竖直滚动开始行
            self.write_cmd(vEnd)#竖直滚动结束行
        
        self.write_cmd(0x29+direction)#水平滚动方向向右
        self.write_cmd(hScrollOn) # 0,关闭水平滚动，1开启
        self.write_cmd(hScrollStartPage)# 水平滚动起始页
        self.write_cmd(hSpeed)#设置滚动速度0-7
        self.write_cmd(hScrollEndPage)# 水平滚动结束页
        self.write_cmd(vSpeed) # 每一帧的垂直偏移量
        self.write_cmd(hScrollStartColumn)#水平滚动区域的起始列
        self.write_cmd(hScrollEndColumn)#水平滚动区域的结束列
        self.write_cmd(0x2f)# 开启滚动
        
    #关闭oled
    def poweroff(self):
        self.write_cmd(0xae | 0x00)#熄屏
    #亮度，0x00-0xff
    def contrast(self, contrast):
        self.write_cmd(0x81)
        self.write_cmd(contrast)
    #正反相显示，输入1则反相，默认正相
    def invert(self, invert=0):
        self.write_cmd(0xa6 | invert)
    # 显示
    def show(self):
        self.write_cmd(0x21) # 告诉GDDRAM列数
        self.write_cmd(0) # 列数从0-127
        self.write_cmd(127)
        self.write_cmd(0x22) # 告诉GDDRAM行数
        self.write_cmd(0) # 页数从0-7
        self.write_cmd(7)
        self.write_framebuf() # 写入1bit地址和1024bit数据
    # 水平翻转,0翻转，1正常（默认）
    def hv(self,b=1):
        self.write_cmd(0xc0 | b<<3)
    #竖直翻转,0翻转，1正常（默认）    
    def vv(self,b=1):
        self.write_cmd(0xa0|b)
    #刷新缓冲区
    def fill(self, c):
        self.framebuf.fill(c)
    #画点，默认点亮，置0则暗
    def pixel(self, x, y, c=1):
        self.framebuf.pixel(x, y, c)
    #写字符
    def text(self, s, x, y, c=1):
        self.framebuf.text(s, x, y, c)
    #画水平直线
    def hline(self,x,y,w,c=1):
        self.framebuf.hline(x,y,w,c)
    #画竖直直线
    def vline(self,x,y,h,c=1):
        self.framebuf.vline(x,y,h,c)
    #画任意直线 
    def line(self,x1,y1,x2,y2,c=1):
        self.framebuf.line(x1,y1,x2,y2,c)
    #画矩形，参数：起始左上角坐标，长宽，颜色默认为亮，是否填充
    def rect(self,x,y,w,h,c=1,f=False):
        self.framebuf.rect(x,y,w,h,c,f)
    #画椭圆，参数：起始圆心坐标，x半径，y半径，颜色默认为亮，是否填充，显示象限（0-15的数字）
    def ellipse(self,x,y,xr,yr,c=1,f=False,m=15):
        self.framebuf.ellipse(x,y,xr,yr,c,f,m)
    #画立方体，左上前点的坐标，边长
    def cube(self,x,y,l):
        self.rect(x,y,l,l)
        self.rect(x+int(0.5*l),int(y-0.5*l),l,l)
        self.line(x,y,int(x+0.5*l),int(y-0.5*l))
        self.line(x+l-1,y,int(x+1.5*l-1),int(y-0.5*l))
        self.line(x-1,y+l,int(x+0.5*l),int(y+0.5*l-1))
        self.line(x+l-1,y+l-1,int(x+1.5*l-1),int(y+0.5*l-1))
    #画8*8的图，列行
    def p8(self,page,x,y):
        for e in range(8):
            byte=bin(page[e]).replace('0b','')
            while len(byte)<8:
                byte='0'+byte
            for i in range(8):
                if byte[i]=='1':
                    self.pixel(x+e,y+i,int(byte[i]))
    #画16*16的图，列行
    def p16(self,page,x,y):
        for e in range(32):
            byte=bin(page[e]).replace('0b','')
            while len(byte)<8:
                byte='0'+byte
            for i in range(8):
                if byte[i] and e<16:
                    self.pixel(x+e,y+i,int(byte[i]))
                elif byte[i] and e>=16:
                    self.pixel(x-16+e,y+8+i,int(byte[i]))
    #画32*32的图，列行
    def p32(self,page,x,y):
        for e in range(128):
            byte=bin(page[e]).replace('0b','')
            while len(byte)<8:
                byte='0'+byte
            for i in range(8):
                if byte[i] and e<32:
                    self.pixel(x+e,y+i,int(byte[i]))
                elif byte[i] and 32<=e<64:
                    self.pixel(x+e-32,y+8+i,int(byte[i]))
                elif byte[i] and 64<=e<96:
                    self.pixel(x+e-64,y+16+i,int(byte[i]))
                elif byte[i] and 96<=e<128:
                    self.pixel(x+e-96,y+24+i,int(byte[i]))
 
class SSD1306_I2C(SSD1306):
    def __init__(self,i2c, addr=0x3c, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        # buffer需要8 * 128的显示字节加1字节命令
        self.buffer = bytearray(8 * 128 + 1)
        self.buffer[0] = 0x40  # Co=0, D/C=1
        self.framebuf = framebuf.FrameBuffer1(memoryview(self.buffer)[1:], 128, 64)
        super().__init__(external_vcc)
    def write_cmd(self, cmd):
        self.temp[0] = 0x80 # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)
 
    def write_framebuf(self):
        self.i2c.writeto(self.addr, self.buffer)
 
'''
示例程序集
#############################
显示ASCII字符
from ssd1306 import SSD1306_I2C
from machine import Pin,I2C
i2c=I2C(0,scl=Pin(5),sda=Pin(4))
oled=SSD1306_I2C(i2c)
 
oled.text('hello world',0,0)
 
oled.show()
#############################
画任意直线
from ssd1306 import SSD1306_I2C
from machine import Pin,I2C
i2c=I2C(0,scl=Pin(5),sda=Pin(4))
oled=SSD1306_I2C(i2c)
 
oled.line(0,2,50,60)
 
oled.show()
#############################
画横线
from ssd1306 import SSD1306_I2C
from machine import Pin,I2C
i2c=I2C(0,scl=Pin(5),sda=Pin(4))
oled=SSD1306_I2C(i2c)
 
oled.hline(2,30,80)
 
oled.show()
#############################
画竖线
from ssd1306 import SSD1306_I2C
from machine import Pin,I2C
i2c=I2C(0,scl=Pin(5),sda=Pin(4))
oled=SSD1306_I2C(i2c)
 
oled.vline(20,0,40)
 
oled.show()
#############################
画矩形
from ssd1306 import SSD1306_I2C
from machine import Pin,I2C
i2c=I2C(0,scl=Pin(5),sda=Pin(4))
oled=SSD1306_I2C(i2c)
#左上角x，y坐标，长，宽
oled.rect(20,0,40,20)
 
oled.show()
#############################
画椭圆
众所周知，圆也是椭圆的一种
from ssd1306 import SSD1306_I2C
from machine import Pin,I2C
i2c=I2C(0,scl=Pin(5),sda=Pin(4))
oled=SSD1306_I2C(i2c)
#参数，中心点x，y坐标，x轴向半径，y轴向半径，f=True为填充，默认不填充
oled.ellipse(20,30,10,20)
oled.ellipse(60,20,10,20,f=True)
 
oled.show()

#还有一个参数非常奇怪，不常用，自己改数字（范围0-15）体会

from ssd1306 import SSD1306_I2C
from machine import Pin,I2C
i2c=I2C(0,scl=Pin(5),sda=Pin(4))
oled=SSD1306_I2C(i2c)
 
oled.ellipse(60,20,10,20,m=5)
 
oled.show()
#############################
画立方体
from ssd1306 import SSD1306_I2C
from machine import Pin,I2C
i2c=I2C(0,scl=Pin(5),sda=Pin(4))
oled=SSD1306_I2C(i2c)
#左前顶面的xy坐标，边长
oled.cube(10,10,20)
 
oled.show()
#############################
画点阵图
from ssd1306 import SSD1306_I2C
from machine import Pin,I2C
i2c=I2C(0,scl=Pin(5),sda=Pin(4))
oled=SSD1306_I2C(i2c)
 
pic=[0x04,0x06,0xFF,0x97,0x57,0x37,0x16,0x04]
#8*8点阵数据，图像左上角xy坐标。16*16，32*32的也一样，只不过改函数名oled.p16()而已
oled.p8(pic,30,30)
 
oled.show()
#############################
翻转
from ssd1306 import SSD1306_I2C
from machine import Pin,I2C
i2c=I2C(0,scl=Pin(5),sda=Pin(4))
oled=SSD1306_I2C(i2c)
 
pic1=[0x00,0x00,0x0F,0x08,0x08,0x08,0x08,0xFF,0x08,0x08,0x08,0x08,0x0F,0x00,0x00,0x00,
0x00,0x00,0xF0,0x20,0x20,0x20,0x20,0xFF,0x20,0x20,0x20,0x20,0xF0,0x00,0x00,0x00]
 
pic2=[0x00,0x7F,0x40,0x48,0x49,0x49,0x49,0x4F,0x49,0x49,0x49,0x48,0x40,0x7F,0x00,0x00,
0x00,0xFF,0x02,0x12,0x12,0x12,0x12,0xF2,0x12,0x52,0x32,0x12,0x02,0xFF,0x00,0x00]
 
oled.p16(pic1,0,0)
oled.p16(pic2,16,0)
oled.show()
#以中心竖直轴翻转，填1则正常显示
oled.vv(0)
#########################################################################
也是翻转
from ssd1306 import SSD1306_I2C
from machine import Pin,I2C
i2c=I2C(0,scl=Pin(5),sda=Pin(4))
oled=SSD1306_I2C(i2c)
 
pic1=[0x00,0x00,0x0F,0x08,0x08,0x08,0x08,0xFF,0x08,0x08,0x08,0x08,0x0F,0x00,0x00,0x00,
0x00,0x00,0xF0,0x20,0x20,0x20,0x20,0xFF,0x20,0x20,0x20,0x20,0xF0,0x00,0x00,0x00]
 
pic2=[0x00,0x7F,0x40,0x48,0x49,0x49,0x49,0x4F,0x49,0x49,0x49,0x48,0x40,0x7F,0x00,0x00,
0x00,0xFF,0x02,0x12,0x12,0x12,0x12,0xF2,0x12,0x52,0x32,0x12,0x02,0xFF,0x00,0x00]
 
oled.p16(pic1,0,0)
oled.p16(pic2,16,0)
oled.show()
#以中心水平轴翻转
oled.hv(0)
#############################
反相
from ssd1306 import SSD1306_I2C
from machine import Pin,I2C
i2c=I2C(0,scl=Pin(5),sda=Pin(4))
oled=SSD1306_I2C(i2c)
 
pic1=[0x00,0x00,0x0F,0x08,0x08,0x08,0x08,0xFF,0x08,0x08,0x08,0x08,0x0F,0x00,0x00,0x00,
0x00,0x00,0xF0,0x20,0x20,0x20,0x20,0xFF,0x20,0x20,0x20,0x20,0xF0,0x00,0x00,0x00]
 
pic2=[0x00,0x7F,0x40,0x48,0x49,0x49,0x49,0x4F,0x49,0x49,0x49,0x48,0x40,0x7F,0x00,0x00,
0x00,0xFF,0x02,0x12,0x12,0x12,0x12,0xF2,0x12,0x52,0x32,0x12,0x02,0xFF,0x00,0x00]
 
oled.p16(pic1,0,0)
oled.p16(pic2,16,0)
oled.show()
#默认不反相，即默认0
oled.invert(1)
#############################
滚动
横向滚动
from ssd1306 import SSD1306_I2C
from machine import Pin,I2C
i2c=I2C(0,scl=Pin(5),sda=Pin(4))
oled=SSD1306_I2C(i2c)
 
pic1=[0x00,0x00,0x0F,0x08,0x08,0x08,0x08,0xFF,0x08,0x08,0x08,0x08,0x0F,0x00,0x00,0x00,
0x00,0x00,0xF0,0x20,0x20,0x20,0x20,0xFF,0x20,0x20,0x20,0x20,0xF0,0x00,0x00,0x00]
 
pic2=[0x00,0x7F,0x40,0x48,0x49,0x49,0x49,0x4F,0x49,0x49,0x49,0x48,0x40,0x7F,0x00,0x00,
0x00,0xFF,0x02,0x12,0x12,0x12,0x12,0xF2,0x12,0x52,0x32,0x12,0x02,0xFF,0x00,0x00]
 
oled.p16(pic1,0,0)
oled.p16(pic2,16,0)
oled.show()
#默认整个页面一起滚动
#参数：
#滚动起始页，滚动结束页
#滚动方向（默认向左，填0向右）
#滚动速度（0-7，默认0，不一定数字越大速度越大）
oled.h_scroll()
#############################
纵向滚动
目前我只能实现向上滚，还有点bug

from ssd1306 import SSD1306_I2C
from machine import Pin,I2C
i2c=I2C(0,scl=Pin(5),sda=Pin(4))
oled=SSD1306_I2C(i2c)
 
pic1=[0x00,0x00,0x0F,0x08,0x08,0x08,0x08,0xFF,0x08,0x08,0x08,0x08,0x0F,0x00,0x00,0x00,
0x00,0x00,0xF0,0x20,0x20,0x20,0x20,0xFF,0x20,0x20,0x20,0x20,0xF0,0x00,0x00,0x00]
 
pic2=[0x00,0x7F,0x40,0x48,0x49,0x49,0x49,0x4F,0x49,0x49,0x49,0x48,0x40,0x7F,0x00,0x00,
0x00,0xFF,0x02,0x12,0x12,0x12,0x12,0xF2,0x12,0x52,0x32,0x12,0x02,0xFF,0x00,0x00]
 
oled.p16(pic1,0,0)
oled.p16(pic2,16,0)
oled.show()
oled.scroll(hScrollOn=0)
#############################
奇葩滚动
这个函数比较复杂可实现斜着动，不同区域各动各的，有点bug
from ssd1306 import SSD1306_I2C
from machine import Pin,I2C
i2c=I2C(0,scl=Pin(5),sda=Pin(4))
oled=SSD1306_I2C(i2c)
 
pic1=[0x00,0x00,0x0F,0x08,0x08,0x08,0x08,0xFF,0x08,0x08,0x08,0x08,0x0F,0x00,0x00,0x00,
0x00,0x00,0xF0,0x20,0x20,0x20,0x20,0xFF,0x20,0x20,0x20,0x20,0xF0,0x00,0x00,0x00]
 
pic2=[0x00,0x7F,0x40,0x48,0x49,0x49,0x49,0x4F,0x49,0x49,0x49,0x48,0x40,0x7F,0x00,0x00,
0x00,0xFF,0x02,0x12,0x12,0x12,0x12,0xF2,0x12,0x52,0x32,0x12,0x02,0xFF,0x00,0x00]
 
oled.p16(pic1,0,0)
oled.p16(pic2,16,0)
oled.show()
#10个参数。均有默认值
#vScrollOn，是否开启竖直滚动（默认0，关闭竖直滚动；置1开启）
#vStart，竖直滚动开始行
#vEnd，竖直滚动结束行
#vSpeed，竖直滚动速度，数字越大越快
#hScrollOn，是否开启横向滚动（默认开启，置0关闭）
#direction，横滚方向（默认向右，置1向左）
#hSpeed，横滚速度（0-7）
#hScrollStartPage，水平滚动起始页默认0
#hScrollEndPage，水平滚动结束页默认7
#hScrollStartColumn，水平滚动区域的起始列，默认0
#hScrollEndColumn，#水平滚动区域的结束列，默认127
oled.scroll()
#############################
'''
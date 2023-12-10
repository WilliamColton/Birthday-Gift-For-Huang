import ssd1306
class Screen(ssd1306.SSD1306_I2C):

    def __init__(self,screen_length,screen_width,i2c):
        self.x=screen_length
        self.y=screen_width
        self.i2c=i2c
        
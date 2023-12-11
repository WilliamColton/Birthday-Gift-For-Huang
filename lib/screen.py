import ssd1306

class Screen(ssd1306.SSD1306_I2C):

    def __init__(self, i2c, addr=60, external_vcc=False):
        super().__init__(i2c, addr, external_vcc)
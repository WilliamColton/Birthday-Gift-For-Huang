import screen

def IsCollision(location_a,location_b):
    '发生碰撞即返回True'
    if location_a==location_b:
        return True

class GameEngine(screen.Screen):

    def __init__(self, i2c, addr=60, external_vcc=False):
        super().__init__(i2c, addr, external_vcc)

    def start(self):
        pass

    def update(self):
        pass


class GameObject(GameEngine):
    def __init__(self, screen_x, screen_y,x,y,type):
        super().__init__(screen_x, screen_y)
        self.x=x
        self.y=y
        self.type=type
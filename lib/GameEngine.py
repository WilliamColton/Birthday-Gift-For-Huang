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
    def __init__(self, i2c, addr=60, external_vcc=False):
        super().__init__(i2c, addr, external_vcc)
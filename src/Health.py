from ECS import *


class Health(Component):

    def __init__(self, hp):
        super().__init__("health")
        self.maxhp = hp
        self.hp = hp



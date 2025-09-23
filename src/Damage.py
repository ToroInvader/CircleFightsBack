from mouseinfo import position

from ECS import *
import Vector

"""might wanna a kb component and a kb resistance component then link it dmg system accordingly if you want more advanced kb(like bosses take less kb)"""


class Damage(Component):
    def __init__(self, dmg):
        super().__init__("damage")
        self.dmg = dmg

class KnockBack(Component):
    def __init__(self, kb):
        super().__init__("knockback")
        self.kb = kb


class Knockbackable(Component):

    def __init__(self, resistance): # a number between 1 and 0 the higher the number the more resistance it has
        super().__init__('knockbackable')
        self.resistance = 1-resistance

# just focuses on dishing out damage and maybe kb if an object has physics
class DamageSystem():

    def tick(self, ecs: ECS, events):
        for event in events["enter"]:
            id1 = event[0]
            id2 = event[1]
            if ecs.has_component(id1, "damage"):
                damage1 = ecs.get_component(id1, "damage")
                if ecs.has_component(id2, "health"):
                    health2 = ecs.get_component(id2, "health")
                    health2.hp -= damage1.dmg
            #apply kb if possible
            if ecs.has_component(id2, "physics", "position", "knockbackable") and ecs.has_component(id1, "position", "knockback"): # what if i get invincible enemies or it could be better to make this it's own system
                position1 = ecs.get_component(id1, "position")
                knockback1 = ecs.get_component(id1, "knockback")
                position2 = ecs.get_component(id2, "position")
                physics2 =  ecs.get_component(id2, "physics")
                knockbackable2 =  ecs.get_component(id2, "knockbackable")
                direction = Vector.Unit(Vector.Subtract(position2.position, position1.position))
                physics2.forces.append(Vector.scalarMult(knockback1.kb*knockbackable2.resistance, direction))








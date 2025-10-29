from ECS import *
from Global import *

#may want to complexify by adding stamina cooldowns and such so players have to manage stamina more wisely

class Stamina(Component):

    def __init__(self, maxStamina, staminaRegen, staminaDeath):
        super().__init__("stamina")
        self.maxStamina = maxStamina
        self.stamina = maxStamina
        self.staminaRegen = staminaRegen
        self.staminaDeath = staminaDeath*FPS
        self.isRegen = True
        self.elapsed = 0

class StaminaSystem():
    def tick(self, ecs: ECS):
        for id in ecs.query("stamina"):
            stamina = ecs.get_component(id, "stamina")
            if stamina.stamina < 0 and stamina.isRegen:
                stamina.elapsed = stamina.staminaDeath
                stamina.isRegen = False
                #clamp stamina ig
                stamina.stamina = max(0, stamina.stamina)
            if not stamina.isRegen:
                stamina.elapsed -= 1
                print(stamina.elapsed)
            if stamina.elapsed == 0:
                stamina.isRegen = True
            if stamina.stamina < stamina.maxStamina and stamina.isRegen:
                stamina.stamina += stamina.staminaRegen
                #clamp it down here in case there's an excess amount(in the future i might change this)
                stamina.stamina = min(stamina.stamina, stamina.maxStamina)
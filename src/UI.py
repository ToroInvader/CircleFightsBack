from ECS import *
from Rendering import *
from src.Physics import Position


class globalUIComponent(Component):
    
    def __init__(self, size):
        super().__init__("globalui")
        self.size = size

class StaminaUI(Component):

    def __init__(self):
        super().__init__("staminaui")

class HealthUI(Component):

    def __init__(self):
        super().__init__("healthui")

#setup the UI here
def spawnUI(ecs : ECS, width, height, size):
    globalUIID = ecs.create_entity()
    globalUI = ecs.add_component(globalUIID, globalUIComponent(size))
    outerHealth = ecs.create_entity()
    ecs.add_component(outerHealth,  RenderCircle(globalUI.size,colours["dark red"], False, 2))
    ecs.add_component(outerHealth, Position(width-(10+globalUI.size),globalUI.size+10))
    health = ecs.create_entity()
    ecs.add_component(health,  RenderCircle(globalUI.size,colours["red"], False, 3))
    ecs.add_component(health, Position(width-(10+globalUI.size),globalUI.size+10))
    ecs.add_component(health, HealthUI())
    outerStamina = ecs.create_entity()
    ecs.add_component(outerStamina,  RenderCircle(globalUI.size,colours["dark green"], False, 2))
    ecs.add_component(outerStamina, Position(width-(10+globalUI.size),3*(globalUI.size+10)))
    stamina = ecs.create_entity()
    ecs.add_component(stamina,  RenderCircle(globalUI.size,colours["green"], False, 3))
    ecs.add_component(stamina, Position(width-(10+globalUI.size),3*(globalUI.size+10)))
    ecs.add_component(stamina, StaminaUI())



class UISystem: #UI handled by this thing

    def tick(self, ecs: ECS): #uiid here means user interface and then id not some unique id
        #grab player
        playerID = next(iter(ecs.query("player")))
        healthUIID = next(iter(ecs.query("healthui")))
        staminaUIID = next(iter(ecs.query("staminaui")))
        globalUIID = next(iter(ecs.query("globalui")))
        playerStamina = ecs.get_component(playerID, "stamina")
        playerHealth = ecs.get_component(playerID, "health")
        staminaUI = ecs.get_component(staminaUIID, "render")
        healthUI = ecs.get_component(healthUIID, "render")
        globalComp = ecs.get_component(globalUIID, "globalui")

        healthUI.r = (playerHealth.hp/playerHealth.maxhp)*globalComp.size
        staminaUI.r = (playerStamina.stamina/playerStamina.maxStamina)*globalComp.size


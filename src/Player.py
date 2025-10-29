from Input import *
from CollisionResolvement import *
from Effect import *
from Aura import *
from Damage import *
from Stamina import *
from src.Health import Health


class PlayerComponent(Component):
    def __init__(self, dashStrength, dashConsumption):
        super().__init__("player")
        self.dashStrength = dashStrength
        self.dashConsumption = dashConsumption

class PlayerSystem:

    def tick(self, ecs: ECS):
        #handle everything a player would do
        eid = next(iter(ecs.query("player")))
        player = ecs.get_component(eid, "player")
        inputComp = ecs.get_component(eid, "input")
        physicsComp = ecs.get_component(eid, "physics")
        motorComp = ecs.get_component(eid, "motorforce")
        staminaComp = ecs.get_component(eid, "stamina")
        force = Vector.scalarMult(motorComp.strength, inputComp.inputDir)
        if inputComp.canDash and Vector.Magnitude(inputComp.inputDir) > 0 and staminaComp.stamina > 0:
            force = Vector.scalarMult(player.dashStrength * motorComp.strength, inputComp.inputDir)
            staminaComp.stamina -= player.dashConsumption
            #add aura component here
            ecs.add_component(eid, AuraComponent(0.25, 3, 0.25))
        physicsComp.forces.append(force)

    def getPlayerPos(self, ecs:ECS):
        eid =  next(iter(ecs.query("player")))
        pos = ecs.get_component(eid, "position")
        return pos.position

def spawnPlayer(ecs: ECS):
    eid = ecs.create_entity()
    size = 20
    width = 40
    height = 40
    points = [[-20,5],[10,20],[0,-30],[-10,20],[20,5]]
    ecs.add_component(eid, PlayerComponent(100, 20))
    ecs.add_component(eid, Position(0,0))
    ecs.add_component(eid, Velocity(0,0))
    ecs.add_component(eid, Physics(20, dragFactor=1))
    ecs.add_component(eid, MotorForce(5))
    ecs.add_component(eid, RenderCircle(size, colours["red"], True))
    ecs.add_component(eid, CollisionCircle(size))
    ecs.add_component(eid, InputComponent())
    ecs.add_component(eid, RigidBody())
    ecs.add_component(eid, Material(1))
    ecs.add_component(eid, Damage(1))
    ecs.add_component(eid, Knockbackable(0))
    ecs.add_component(eid, Stamina(100, 0.1, 1))
    ecs.add_component(eid, Health(100))






from Input import *
from CollisionResolvement import *
from Effect import *
from Aura import *
from Damage import *


class PlayerComponent(Component):
    def __init__(self, dashStrength):
        super().__init__("player")
        self.dashStrength = dashStrength

class PlayerSystem:

    def tick(self, ecs: ECS):
        #handle everything a player would do
        eid = next(iter(ecs.query("player")))
        player = ecs.get_component(eid, "player")
        inputComp = ecs.get_component(eid, "input")
        physicsComp = ecs.get_component(eid, "physics")
        motorComp = ecs.get_component(eid, "motorforce")
        force = Vector.scalarMult(motorComp.strength, inputComp.inputDir)
        if inputComp.canDash:
            force = Vector.scalarMult(player.dashStrength * motorComp.strength, inputComp.inputDir)
            #add aura component here
            ecs.add_component(eid, AuraComponent(0.25, 3, 0.25))
        physicsComp.forces.append(force)

    def getPlayerPos(self, ecs:ECS):
        eid =  next(iter(ecs.query("player")))
        pos = ecs.get_component(eid, "position")
        return pos.position

def spawnPlayer(self, ecs: ECS):
    eid = ecs.create_entity()
    size = 20
    width = 40
    height = 40
    points = [[-20,5],[10,20],[0,-30],[-10,20],[20,5]]
    ecs.add_component(eid, PlayerComponent(100))
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







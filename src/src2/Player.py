

from ECS import *
from Collision import *
from Physics import *
from Rendering import *
from Input import *
from Physics import *
from CollisionResolvement import *
from  Timer import *
import Vector
from Effect import *


class PlayerComponent(Component):
    def __init__(self, dashStrength):
        super().__init__("player")
        self.dashStrength = dashStrength

class PlayerSystem:

    def tick(self, ecs: ECS):
        #handle everything a player would do
        eids = ecs.query("player")
        for eid in eids:
            player = ecs.get_component(eid, "player")
            inputComp = ecs.get_component(eid, "input")
            physicsComp = ecs.get_component(eid, "physics")
            motorComp = ecs.get_component(eid, "motorforce")
            timerComp = ecs.get_component(eid, "timer")
            positionComp = ecs.get_component(eid, "position")
            force = Vector.scalarMult(motorComp.strength,inputComp.inputDir)
            if inputComp.canDash:
                force = Vector.scalarMult(player.dashStrength*motorComp.strength,inputComp.inputDir)
                timerComp.add(0.25 ,"dashing")
            physicsComp.forces.append(force)
            #effect management
            for t in timerComp.active:
                if t[2] == "dashing":
                    if t[1] % 3 == 0:
                        createEffect(ecs, positionComp.position[0], positionComp.position[1], [[-20,5],[10,20],[0,-30],[-10,20],[20,5]], "polygon", colours["blue"], 0,0,0.5,True)

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
        ecs.add_component(eid, RenderPolygon(points, colours["red"], True))
        ecs.add_component(eid, CollisionPolygon(points))
        ecs.add_component(eid, InputComponent())
        ecs.add_component(eid, RigidBody())
        ecs.add_component(eid, Material(1))
        ecs.add_component(eid, Timer())







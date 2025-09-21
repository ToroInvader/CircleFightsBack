
import Vector
from ECS import *
from src2.Vector import scalerDiv


class Position(Component):
    def __init__(self, x, y):
        super().__init__("position")
        self.position = [x,y]

class Velocity(Component):
    def __init__(self,x,y):
        super().__init__("velocity")
        self.velocity = [x,y]

class Physics(Component):
    def __init__(self, mass, dragFactor=1, localGravityScale=1):
        super().__init__("physics")
        self.forces = []  # the forces active on it
        self.mass = mass
        self.dragFactor = dragFactor
        self.localGravityScale = localGravityScale # I ain't adding gravity either way just here for the vibes (in case I want global gravity in some funky direction)
        self.acceleration = [0.0,0.0]
        self.resultantForce = [0.0,0.0]  # sum of forces

# determines the strength of internal movement(object itself caused the movement like player input)
class MotorForce(Component):
    def __init__(self, strength):
        super().__init__("motorforce")
        self.strength = strength

class GlobalPhysics(Component):

    def __init__(self, gravityStrength=1, gravityDir=None, drag=1):
        super().__init__("globalphysics")
        if gravityDir is None:
            gravityDir = [0, 0]
        self.gravityStrength=gravityStrength
        self.gravityDir = gravityDir # defaulting it to [0,0] should ensure no use of gravity
        self.drag = drag

class PhysicsSystem:


    def __init__(self, ecs:ECS, gravityStrength=1, gravityDir=None, drag=1):# these are environmental things
        eid = ecs.create_entity()
        ecs.add_component(eid,GlobalPhysics(gravityStrength, gravityDir, drag))

    def tick(self, ecs: ECS):
        globalPhysics = ecs.get_component(next(iter(ecs.query("globalphysics"))),  "globalphysics")

        for eid in ecs.query("physics", "velocity"):
            physic = ecs.get_component(eid, "physics")
            velocity = ecs.get_component(eid, "velocity")
            self.enforceEnvironment(physic, velocity, globalPhysics)
            self.updateAcelerations(physic)
            self.updateVelocity(physic, velocity)
        for eid in ecs.query("velocity", "position"):
            velocity = ecs.get_component(eid, "velocity")
            position = ecs.get_component(eid, "position")
            self.updatePosition(velocity, position)

    def enforceEnvironment(self, p, v, g): #weird name but it just means adding environmental force like gravity and resistance
        dragForce = Vector.scalarMult(-1*(p.dragFactor*g.drag), v.velocity)
        gravityForce = Vector.scalarMult(g.gravityStrength*p.localGravityScale,g.gravityDir)
        p.forces.append(dragForce)
        p.forces.append(gravityForce)

    @staticmethod
    def updateAcelerations(p):
        p.resultantForce = PhysicsSystem.findResultant(p)
        p.forces = []
        p.acceleration = scalerDiv(p.resultantForce, p.mass)

    @staticmethod
    def updateVelocity(p,vel):
        vel.velocity = Vector.Add(p.acceleration, vel.velocity)

    @staticmethod
    def updatePosition(vel, pos):
        pos.position = Vector.Add(vel.velocity, pos.position)

    @staticmethod
    def resetPhysics(p):
        p.resultantForce = 0
        p.forces = []
        p.acceleration = [0.0,0.0]

    @staticmethod
    def setVelocity(vel, x, y):
        vel.velocity = [x,y]

    @staticmethod
    def setPosition(pos, x, y):
        pos.position = [x,y]

    @staticmethod
    def findResultant(p):
        return Vector.Sum(p.forces)



import math
import random

from  ECS import *
from Collision import *
from Rendering import *
from Physics import *
from CollisionResolvement import *
import Vector
from Damage import *


#region general enemy stuff

class Enemy(Component): # A glorified tag for now(like what do i put here?)

    def __init__(self):
        super().__init__("enemy")

#make sure to allow customisation for specific enemies and add adjust local drag factors for more interesting behaviours like(acceleration)
def spawnEnemy(ecs, x, y, width, height, mass, speed, kb, damage, type, colour):
    eid = ecs.create_entity()
    ecs.add_component(eid, CollisionRect(width, height))
    ecs.add_component(eid, RenderRect(width, height, colour, True, 0))
    ecs.add_component(eid, Position(x, y))
    ecs.add_component(eid, Velocity(0, 0))
    ecs.add_component(eid, Physics(mass))
    motorforce = ecs.add_component(eid, MotorForce(speed))
    ecs.add_component(eid, RigidBody())
    ecs.add_component(eid, Material(0))
    ecs.add_component(eid, KnockBack(kb))
    ecs.add_component(eid, Damage(damage))
    if(type=="pursuer"):
        ecs.add_component(eid, Pursuer())
    elif(type=="straightpursuer"):
        ecs.add_component(eid, StraightPursuer())
    elif type=="spiralin":
        ecs.add_component(eid, SpiralIn())
    elif type=="burster":
        ecs.add_component(eid, Burster(random.randint(1,5),10))
        motorforce.strength = speed*speed
    elif type=="looker":
        ecs.add_component(eid, Looker([random.randint(-300,300), random.randint(-300,300)]))
    elif type=="teleporter":
        ecs.add_component(eid, Teleporter(1, 1000))
    ecs.add_component(eid, StraightPursuer())
    #else dummy AI ig

#endregion

#region movement patterns
class Pursuer(Component):  #an AI that always chases the player

    def __init__(self):
        super().__init__("pursuer")

class PursuerSystem:

    def tick(self, ecs: ECS):
        #grab the player position
        eid = next(iter(ecs.query("player")))
        playerPos = ecs.get_component(eid, "position")
        for id in ecs.query("pursuer", "position","physics", "motorforce"):
            enemyPos =  ecs.get_component(id, "position")
            enemyPhysics = ecs.get_component(id, "physics")
            enemyMotor = ecs.get_component(id, "motorforce")
            direction = Vector.Unit(Vector.Subtract(playerPos.position, enemyPos.position))
            enemyPhysics.forces.append(Vector.scalarMult(enemyMotor.strength, direction))

class StraightPursuer(Component):

    def __init__(self):
        super().__init__("straightpursuer")

class StraightPursuerSystem():

    def tick(self, ecs: ECS):
        # grab the player position
        eid = next(iter(ecs.query("player")))
        playerPos = ecs.get_component(eid, "position")
        for id in ecs.query("straightpursuer", "position", "physics", "velocity","motorforce"):
            enemyPos = ecs.get_component(id, "position")
            enemyPhysics = ecs.get_component(id, "physics")
            enemyVelocity = ecs.get_component(id, "velocity")
            enemyMotor = ecs.get_component(id, "motorforce")
            xDiff = playerPos.position[0] - enemyPos.position[0]
            yDiff = playerPos.position[1] - enemyPos.position[1]
            if abs(xDiff) > abs(yDiff):
                enemyPhysics.forces.append(Vector.scalarMult(enemyMotor.strength,[math.copysign(1,xDiff), 0]))
                enemyVelocity.velocity[1] = 0
            else:
                enemyPhysics.forces.append(Vector.scalarMult(enemyMotor.strength,[0, math.copysign(1,yDiff)]))
                enemyVelocity.velocity[0] = 0

class SpiralIn(Component):

    def __init__(self):
        super().__init__("spiralin")
        self.orientation = 1 if random.randint(1,2)==1 else -1 # an integer 1 for clockwise i think and -1 for counter clockwise


class SpiralInSystem():
    def tick(self, ecs):
        # grab the player position
        eid = next(iter(ecs.query("player")))
        playerPos = ecs.get_component(eid, "position")
        for id in ecs.query("spiralin", "position", "physics", "motorforce"):
            enemyPos = ecs.get_component(id, "position")
            enemyPhysics = ecs.get_component(id, "physics")
            enemyMotor = ecs.get_component(id, "motorforce")
            spiralIn = ecs.get_component(id, "spiralin")
            direction = Vector.Unit(Vector.Subtract(playerPos.position, enemyPos.position))
            normal = Vector.scalarMult(spiralIn.orientation, Vector.Normal(direction))
            trueDirection = Vector.Unit(Vector.Add(direction, normal))
            enemyPhysics.forces.append(Vector.scalarMult(enemyMotor.strength, trueDirection))

class Burster(Component):

    def __init__(self, delay, strength):
        super().__init__("burster")
        self.elapsed = 0
        self.delay = delay*FPS
        self.strength = strength

class BursterSystem():

    def tick(self, ecs):
        eid = next(iter(ecs.query("player")))
        playerPos = ecs.get_component(eid, "position")
        for id in ecs.query("burster", "position", "physics", "motorforce"):
            enemyPos =  ecs.get_component(id, "position")
            enemyPhysics = ecs.get_component(id, "physics")
            enemyMotor = ecs.get_component(id, "motorforce")
            enemyBurster = ecs.get_component(id, "burster")
            enemyBurster.elapsed += 1
            if enemyBurster.delay <= enemyBurster.elapsed:
                enemyBurster.elapsed = 0
                direction = Vector.Unit(Vector.Subtract(playerPos.position, enemyPos.position))
                enemyPhysics.forces.append(Vector.scalarMult(enemyMotor.strength*enemyMotor.strength, direction))


class Looker(Component):

    def __init__(self, relPosition):
        super().__init__("looker")
        self.relPosition = relPosition

class LookerSystem:

    def tick(self, ecs: ECS):
        #grab the player position
        eid = next(iter(ecs.query("player")))
        playerPos = ecs.get_component(eid, "position")
        for id in ecs.query("looker", "position","physics", "motorforce"):
            enemyPos =  ecs.get_component(id, "position")
            enemyPhysics = ecs.get_component(id, "physics")
            enemyMotor = ecs.get_component(id, "motorforce")
            enemyLooker = ecs.get_component(id, "looker")
            lookPos = Vector.Add(playerPos.position, enemyLooker.relPosition)
            direction = Vector.Unit(Vector.Subtract(lookPos, enemyPos.position))
            enemyPhysics.forces.append(Vector.scalarMult(enemyMotor.strength, direction))
#endregion

class Teleporter(Component):

    def __init__(self, delay, distance):
        super().__init__("teleporter")
        self.elapsed = 0
        self.delay = delay*FPS
        self.distance = distance # let's say 10 for now


class TeleporterSystem:

    def tick(self, ecs: ECS):
        eid = next(iter(ecs.query("player")))
        playerPos = ecs.get_component(eid, "position")
        for id in ecs.query("teleporter"):
            enemyPos =  ecs.get_component(id, "position")
            enemytele =  ecs.get_component(id, "teleporter")
            enemytele.elapsed += 1
            if enemytele.delay <= enemytele.elapsed:
                enemytele.elapsed = 0
                direction = Vector.Unit(Vector.Subtract(playerPos.position, enemyPos.position))
                enemyPos.position = Vector.Add(enemyPos.position, Vector.scalarMult(enemytele.distance,direction))



#region element components


#endregion


#reigon Enemy System

class EnemySystem():
    pass

#endregion
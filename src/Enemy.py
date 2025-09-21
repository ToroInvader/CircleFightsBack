from Entity import  * #enemies are composed from entity
from  ECS import *

#our enemy entity
class Enemy(Entity): #all enemies are squares i don't care about your opinion

    collider: CollisionRect  # tell the IDE the refined type

    def __init__(self, x, y, width, height, mass, force, dmg, hp, kb, localInvincibility, AI, element, colour):
        super().__init__(CollisionRect(width,height), x, y, mass, colour)
        self.collider : CollisionRect # cast into it a collisionRect
        self.element = element #objective convert to an ecs approach instead of text
        self.dmg = dmg
        self.force = force
        self.hp = hp
        self.kb = kb # good ol knockback
        self.AI = AI
        self.direction = np.empty(2)
        self.localInvincibility = localInvincibility
        self.hits = {}

#region movement patterns
class Pursuer():  #an AI that always chases the player

    def __init__(self):
        self.type = "Pursuer"

    def move(self, ownX, ownY ,px, py): #player x and player y for px and py respectively position returns a 2d unit vector also
        dmovement = np.array([px - ownX, py - ownY])
        dmovement /= np.linalg.norm(dmovement) # I don't think this will ever be 0
        return dmovement

class StraightPursuer():

    def __init__(self):
        self.type = "StraightPursuer"

    def move(self, ownX, ownY ,px, py): #player x and player y for px and py respectively position returns a 2d unit vector also
        dx = px - ownX
        dy = py - ownY
        if abs(dx) > abs(dy):
            dmovement = np.array([dx, 0])
        else:
            dmovement = np.array([0, dy])

        dmovement /= np.linalg.norm(dmovement)
        return dmovement

class SpiralIn():


    def __init__(self, clockwise): # a boolean to change directions
        self.clockwise = clockwise
        self.type = "SpiralIn"

    def move(self, ownX, ownY, px, py):
        dmovement = np.array([px - ownX, py - ownY])
        if np.linalg.norm(dmovement) > 2200: # the code exist due to escaping nature of some of the enemies that don't circle in fast enough if they're far away to the point some go outer bounds
            dmovement /= np.linalg.norm(dmovement)
            return  dmovement*5
        perpDmovement = np.array([-dmovement[1], dmovement[0]])
        if self.clockwise:
            perpDmovement *= -1
        dmovement = np.add(dmovement, perpDmovement)
        dmovement /= np.linalg.norm(dmovement)
        return  dmovement

class Burster():


    def __init__(self, delay, strength):
        self.type = "Burster"
        self.time = 0
        self.delay = delay
        self.strength = strength

    def move(self, ownX, ownY, px, py):
        self.time += 1
        dmovement = np.array([px - ownX, py - ownY])
        dmovement /= np.linalg.norm(dmovement)
        if(self.time == self.delay):
            self.time = 0
            return dmovement*self.strength
        else:
            return  np.array([0,0])

class Looker():

    def __init__(self, position):
        self.position = position

    def move(self, ownX, ownY ,px, py): #player x and player y for px and py respectively position returns a 2d unit vector also
        px += self.position[0]
        py += self.position[1]
        dmovement = np.array([px - ownX, py - ownY])
        dmovement /= np.linalg.norm(dmovement) # I don't think this will ever be 0
        return dmovement
#endregion

#region element components


#endregion


#reigon Enemy System

class EnemySystem():

    @staticmethod
    def Spawn(x,y,mass):
        eid = ECS.create_entity()
        ECS.add_component(eid, physicsComponent(x,y,mass))



#endRegion
#hooks up all the important components together


from Collision import  *
from Rendering import  *
from Physics import *

#base entity the typical thing that all things use

class Entity:  # be very careful with this class it'll utilise physics and collision as composition and return a render class when needed
    # things could get real messy if the class isn't handled correctly
    def __init__(self, collider: CollisionComponent, x, y, mass, colour):
        self.collider = collider
        self.colour = colour
        self.ID = "idk right now still figuring out the kinks"

    def returnRender(self):
        if self.collider.type == "triangle":
            assert isinstance(self.collider, CollisionTriangle)
            return RenderTriangle(self.physics.position[0], self.physics.position[1], self.collider.xs[0],
                                  self.collider.xs[1], self.collider.xs[2], self.collider.ys[0], self.collider.ys[1],
                                  self.collider.ys[2], self.colour)
        elif self.collider.type == "rect":
            assert isinstance(self.collider, CollisionRect)
            return RenderRect(self.physics.position[0], self.physics.position[1], self.collider.width, self.collider.height,
                              self.colour)
        elif self.collider.type == "circle":
            assert  isinstance(self.collider, CollisionCircle)
            return RenderCircle(self.physics.position[0], self.physics.position[1], self.collider.r, self.colour)
        else:
            print("type isn't defined")  # in case something goes wrong



#region variations of entities enemy and effects in its own folder

class Bullet(Entity):

    def __init__(self, collider, x, y, mass, dmg, kb, colour, time, id):
        super().__init__(collider, x, y, mass, colour)
        self.id = id # needed for enemies to have local invincibility when a hit a by a specific bullet but still be able to be hit by another also defines type
        self.time = time
        self.direction = np.array([0,0])
        self.relativePos = np.array([0,0])
        self.dmg = dmg
        self.kb = kb

class PowerUP(Entity):

    #to keep concise and not blown out of proportions powerup generation code will be here

    def __init__(self, collider: CollisionComponent, x, y, mass, colour, type): # they all have circle colliders and same size as circle
        super().__init__(collider, x, y, mass, colour)
        self.type = type
        self.time = 60*5

#insure to change this to field instead of dmg field so I can generalise this(or it might be better chunk down damage as well)
class DmgField(Entity):

    def __init__(self, x, y, width, height, mass ,direction, dmg, kb, colour):
        super().__init__(CollisionRect(width,height),x,y,mass,colour)
        self.direction = direction
        self.dmg = dmg
        self.kb = kb

#endregion
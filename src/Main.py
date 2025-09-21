#whack initial game play setting shouldn't be here but eh

# V 0.1

input("hello circle needs to fight back agaisnt some squares press enter to continue")
inputdiffculty = int(input("what diffculty do you wanna try 1-10  just type a number the lower number the harder the game (5 is recommended, 2 for rush experience)"))
inputPowerSlider = int(input("how frequent should powerups be pick 1-10 (5 is recommended i think, 4 for rush experience i think)"))
inputNumOfEnemies = int(input("how many squares to initially fight off pick any positive integer (5 is recommended, 50 for rush experience)"))
input("to move use WASD and space to dash and q,e,f to attack good luck, press enter to continue")

import random
import pygame
from pygame.locals import *
import numpy as np
pygame.init()


#region classes

#region renderclasses
class RenderObject:

    @staticmethod
    def render(surface, objects):
        for i in objects:
            if i.renderType == "circle":
                pygame.draw.circle(surface, i.colour, (i.renderX, i.renderY), i.r)
            if i.renderType == "rect":
                pygame.draw.rect(surface, i.colour, pygame.Rect(i.renderX, i.renderY, i.width, i.height))
            if i.renderType == "triangle":
                pygame.draw.polygon(surface, i.colour, ((i.xs[0]+i.renderX,i.ys[0]+i.renderY),(i.xs[1]+i.renderX,i.ys[1]+i.renderY),(i.xs[2]+i.renderX,i.ys[2]+i.renderY)))
            if i.renderType == "text":
                surface.blit(i.text, pygame.Rect(i.renderX, i.renderY, i.width, i.height))


    @staticmethod
    def scroll(r, x, y):
        """ this function updates one render object to be in the correct place if they treat x and y position
        to be middle of screen. Basically just implements scrolling. The r here stands for a render object. For no scrolling just make x and y 0
        """

        if r.renderType == "circle" or r.renderType=="rect":
            r.renderX = r.x - x
            r.renderY = r.y - y
        elif r.renderType == "triangle":
            r.renderX =   r.anchorX - x # for triangles think of the render attribute as just values
            r.renderY = r.anchorY - y # to translate the triangle accordingly


    def __init__(self, renderType, colour):
        """quick rant circles need x,y to be centre of themselves that is how they're
        drawn while x,y for rectangles is top left also remember y increases downwards"""
        self.colour = colour
        self.renderType = renderType #what type of object we're drawing

class RenderCircle(RenderObject):

    def __init__(self, x, y, r, colour):
        super().__init__("circle",colour)
        self.x = x
        self.y = y
        self.renderX = x
        self.renderY = y
        self.r = r

class RenderRect(RenderObject):

    def __init__(self, x, y, width, height, colour):
        super().__init__("rect", colour)
        self.x = x
        self.y = y
        self.renderX = x
        self.renderY = y
        self.height = height
        self.width = width

class RenderText(RenderRect):

    def __init__(self,x,y,width,height,colour,size,text):
        super().__init__(x, y, width, height, colour)
        self.font = pygame.font.Font('freesansbold.ttf', size)
        self.renderType = "text"
        self.text =  self.font.render(text, True, colour)

    def changeText(self, text):
        self.text = self.font.render(text, True, self.colour)




class RenderTriangle(RenderObject):

    def __init__(self, anchorX, anchorY, x1, x2, x3, y1, y2, y3, colour): # the set of coordinates indicate the points of the triangle
        super().__init__("triangle", colour)
        self.anchorX = anchorX # after some thinking /i feel like triangles should be translated using these
        self.anchorY = anchorY # anchors(ones on screen could typically have anchor (0,0)) it will allow for more easier fitting(like the physics system)
        self.xs = np.array([x1,x2,x3])
        self.ys = np.array([y1,y2,y3])
        self.renderX = anchorX
        self.renderY = anchorY
#endregion

class physicsObject:

    @staticmethod
    def updatePhysics(p): # p is the physics object we're working with
        p.resultantForce = physicsObject.findResultant(p)
        p.forces =  np.empty((0, 2))
        p.acceleration = p.resultantForce / p.mass
        p.velocity = np.add(p.acceleration, p.velocity)
        p.position = np.add(p.velocity, p.position)

    @staticmethod
    def resetPhysics(p):
        p.resultantForce = 0
        p.forces = np.empty((0,2))
        p.acceleration = np.empty((2))
        p.velocity = np.empty((2))

    @staticmethod
    def findResultant(p):
        return np.sum(p.forces, axis=0)

    def __init__(self, x, y, mass):
        self.position = np.array([x,y])
        self.velocity = np.empty((2))
        self.acceleration = np.empty((2))
        self.resultantForce = np.empty((2))  # sum of forces
        self.forces = np.empty((0, 2)) # the forces active on it
        self.mass = mass

    def addForce(self, force): #force is an np 2d array
        self.forces = np.vstack((self.forces, force))

#region collision object classes hold information about the shape of an object that's it they don't have access to position
# also handles collision
class CollisionObject:

    @staticmethod
    def pointInTriangle(x, y, c, cx, cy): #the maths here get extremely chaotic i'm not explaining it go look up on YouTube how to do this
        Ax = c.xs[0] + cx
        Bx = c.xs[1] + cx
        Cx = c.xs[2] + cx
        Ay = c.ys[0] + cy
        By = c.ys[1] + cy
        Cy = c.ys[2] + cy
        #the variables above exist so I can write the formulas carefully
        denom = ((By-Ay)*(Cx-Ax)-(Bx-Ax)*(Cy-Ay))
        if denom==0:
            return False

        W1 = (Ax*(Cy-Ay)+(y-Ay)*(Cx-Ax)-x*(Cy-Ay))/denom # i hope the code follows BEDMAS order
        W2 = (y-Ay-W1*(By-Ay))/(Cy-Ay)
        return W1 >= 0 and W2 >= 0 and (W1+W2) <= 1


    @staticmethod
    def pointInRect(x, y, c, cx, cy): #c is the collision object with its position as cx and cy
        return ((cx <= x <= cx + c.width) and
                (cy <= y <= cy + c.height))

    @staticmethod
    def pointInCircle(x, y, c, cx, cy):
        euclideanDistance = np.sqrt(((x-cx)**2)+((y-cy)**2))
        return euclideanDistance <= c.r

    @staticmethod
    def linesIntersect(A, B, C, D): #chatgpt made this
        def ccw(P, Q, R):
            return (R[1] - P[1]) * (Q[0] - P[0]) > (Q[1] - P[1]) * (R[0] - P[0])
        return (ccw(A, C, D) != ccw(B, C, D)) and (ccw(A, B, C) != ccw(A, B, D))

    @staticmethod
    def triangleInTriangle(t1px, t1py, t1c, t2px, t2py, t2c): # utilise Separating Axis Theorem if push comes to shove make the code pure python to optimise the code
        # grab points A,B,C for t1 and D,E,F for t2
        A = np.array([t1c.xs[0]+t1px, t1c.ys[0]+t1py])
        B = np.array([t1c.xs[1]+t1px, t1c.ys[1]+t1py])
        C = np.array([t1c.xs[2]+t1px, t1c.ys[2]+t1py])
        D = np.array([t2c.xs[0]+t2px, t2c.ys[0]+t2py])
        E = np.array([t2c.xs[1]+t2px, t2c.ys[1]+t2py])
        F = np.array([t2c.xs[2]+t2px, t2c.ys[2]+t2py])
        # determine unit vectors of separating axes(the nominal vector of each side)
        separatingAxes = []
        AB = A-B
        AB = AB / np.linalg.norm(AB)
        separatingAxes.append(np.array([-AB[1], AB[0]]))
        BC = B-C
        BC = BC / np.linalg.norm(BC)
        separatingAxes.append(np.array([-BC[1], BC[0]]))
        CA = C-A
        CA = CA / np.linalg.norm(CA)
        separatingAxes.append(np.array([-CA[1], CA[0]]))
        DE = D-E
        DE = DE / np.linalg.norm(DE)
        separatingAxes.append(np.array([-DE[1], DE[0]]))
        EF = E-F
        EF = EF / np.linalg.norm(EF)
        separatingAxes.append(np.array([-EF[1], EF[0]]))
        FD = F-D
        FD = FD / np.linalg.norm(FD)
        separatingAxes.append(np.array([-FD[1], FD[0]]))
        # determine the scores(which is length of the vector projected onto the separating axes)
        # of all points for each separating axis
        for i in separatingAxes:
            values1 = []
            values2 = []
            values1.append(np.dot(A, i))
            values1.append(np.dot(B, i))
            values1.append(np.dot(C, i))
            values2.append(np.dot(D, i))
            values2.append(np.dot(E, i))
            values2.append(np.dot(F, i))
            # now check if the max and min compare well if not instantly return false
            t1Max = max(values1)
            t1Min = min(values1)
            t2Max = max(values2)
            t2Min = min(values2)
            if t1Max <= t2Min or t2Max <= t1Min:
                return False
        return True

    @staticmethod #chatgpt made this function and turns out little Tim was right all along this code sucks for small numbers like 100 so the first one will be used
    def triangleInTriangle2(t1px, t1py, t1c, t2px, t2py, t2c):
        #grab points
        t1 = np.array([[t1c.xs[i]+t1px, t1c.ys[i]+t1py] for i in range(3)])
        t2 = np.array([[t2c.xs[i]+t2px, t2c.ys[i]+t2py] for i in range(3)])

        #grab triangle edges
        edges = np.vstack([
             t1[[0,1]], t1[[1,2]], t1[[2,0]],
            t2[[0,1]], t2[[1,2]], t2[[2,0]]
        ]).reshape(6,2,2)

        #now their perpendicular unit vector equivalent
        vecs = edges[:,0] -  edges[:, 1]
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        normals = np.hstack([
            -vecs[:, [1]],
            vecs[:, [0]]
        ]) / norms
        for axis in normals:
            proj1 = t1 @ axis
            proj2 = t2 @ axis
            if proj1.max() <= proj2.min() or proj2.max() <= proj1.min():
                return False  # Separating axis found
        return True



    @staticmethod
    def triangleInRect(tpx, tpy, tc, spx, spy, sc): #t:triangle, s:square, p:position, c:collider

        # grab points
        triPoints = [[tc.xs[i] + tpx, tc.ys[i] + tpy] for i in range(3)]
        quadPoints = [[spx, spy], [spx + sc.width, spy], [spx, spy + sc.height], [spx + sc.width, spy + sc.height]]

        # check if points of triangle in rectangle
        for x,y in triPoints:
            if(CollisionObject.pointInRect(x, y, sc, spx, spy)):
                return True

        #check if points of rectangle in triangle
        for x,y in quadPoints:
            if(CollisionObject.pointInTriangle(x, y, tc, tpx, tpy)):
                return True

        #check if edges are intersecting
        # grab edges
        triEdges = [(triPoints[0], triPoints[1]), (triPoints[1], triPoints[2]), (triPoints[2], triPoints[0])]
        quadEdges = [
            (quadPoints[0], quadPoints[1]),
            (quadPoints[1], quadPoints[2]),
            (quadPoints[2], quadPoints[3]),
            (quadPoints[3], quadPoints[0])
        ]
        for e1 in quadEdges:
            for e2 in triEdges:
                if CollisionObject.linesIntersect(e1[0], e1[1], e2[0], e2[1]):
                    return True
        return False

    @staticmethod
    def triangleInCircle(tpx, tpy, tc, spx, spy, sc):  # t:triangle, s:circle, p:position, c:collider
        return (CollisionObject.pointInCircle(tpx + tc.xs[0], tpy + tc.ys[0], sc, spx, spy) or
                CollisionObject.pointInCircle(tpx + tc.xs[1], tpy + tc.ys[1], sc, spx, spy) or
                CollisionObject.pointInCircle(tpx + tc.xs[2], tpy + tc.ys[2], sc, spx, spy))

    @staticmethod
    def rectInRect(s1px, s1py, s1c, s2px, s2py, s2c): # numbers used to differentiate the colliders
        # keep above code for poking apparently and redundancy ig
        return   (s1px <= s2px+s2c.width and
                  s1c.width+s1px >= s2px and
                  s1py <= s2py+s2c.height  and
                  s1c.height+s1py >= s2py)


    @staticmethod
    def rectInCircle(s1px, s1py, s1c, s2px, s2py, s2c):  # numbers used to differentiate the colliders
        dy = 0
        dx = 0
        if s1py <= s2py <= s1py+s1c.height and s1px <= s2px <= s1px+s1c.width:
            return True # this means the circle is inside the rect
        if s1py <= s2py <= s1py+s1c.height:
            dx = min(abs(s2px - s1px), abs(s2px - (s1px+s1c.width))) #this code might be confusing but it's trying to find the vertical side closer to the circle
            return dy ** 2 + dx ** 2 <= s2c.r ** 2
        elif s1px <= s2px <= s1px+s1c.width:
            dy = min(abs(s2py - s1py), abs(s2py - (s1py+s1c.height))) # same but horizontal
            return dy ** 2 + dx ** 2 <= s2c.r ** 2
        else:
            dx = min(abs(s2px - s1px), abs(s2px - (s1px+s1c.width)))
            dy = min(abs(s2py - s1py), abs(s2py - (s1py+s1c.height)))
            return dy ** 2 + dx ** 2 <= s2c.r ** 2 # see if the closest point found is in the circle via Euclidean distance

    @staticmethod
    def circleInCircle(s1px, s1py, s1c, s2px, s2py, s2c): # most interesting one doesn't rely on point information and least expensive to compute
        euclideanDistance = np.sqrt(((s1px - s2px) ** 2) + ((s1py - s2py) ** 2))
        return euclideanDistance < (s1c.r + s2c.r)



    def __init__(self, type):
        self.type = type

class CollisionCircle(CollisionObject):

    def __init__(self, r):
        super().__init__("circle")
        self.r = r

class CollisionTriangle(CollisionObject):

    def __init__(self, x1, y1, x2, y2, x3, y3):
        super().__init__("triangle")
        self.xs = np.array([x1, x2, x3])
        self.ys = np.array([y1, y2, y3])

        # ensure CounterClockwise property
        Ax, Ay = self.xs[0], self.ys[0]
        Bx, By = self.xs[1], self.ys[1]
        Cx, Cy = self.xs[2], self.ys[2]
        if (Bx - Ax) * (Cy - Ay) - (By - Ay) * (Cx - Ax) < 0:
            # Swap B and C to enforce CCW
            self.xs[1], self.xs[2] = self.xs[2], self.xs[1]
            self.ys[1], self.ys[2] = self.ys[2], self.ys[1]

class CollisionRect(CollisionObject):

    def __init__(self, width, height):
        super().__init__("rect")
        self.width = width
        self.height = height

#endregion collision object classes

class Entity: # be very careful with this class it'll utilise physics and collision as composition and return a render class when needed
              # things could get real messy if the class isn't handled correctly
    def __init__(self, collider: CollisionObject, x, y, mass, colour):
        self.collider = collider
        self.physics = physicsObject(x, y, mass)
        self.colour = colour

    def returnRender(self):
        if self.collider.type == "triangle":
            return RenderTriangle(self.physics.position[0], self.physics.position[1], self.collider.xs[0], self.collider.xs[1], self.collider.xs[2], self.collider.ys[0], self.collider.ys[1], self.collider.ys[2], self.colour)
        elif self.collider.type == "rect":
            return RenderRect(self.physics.position[0], self.physics.position[1], self.collider.width, self.collider.height, self.colour)
        elif self.collider.type == "circle":
            return RenderCircle(self.physics.position[0], self.physics.position[1], self.collider.r, self.colour)
        else:
            print("type isn't defined") # in case something goes wrong


class Effect(Entity): # used to make fancy effects that's it

    def __init__(self, collider, x, y, mass, colour, time, timeDecrease, velocity, fade): #collider is just here for shape information not to detect collisions
        super().__init__(collider, x, y, mass, colour)
        self.totalTime = time # the time it takes for it to decay
        self.time = time
        self.timeDecrease = timeDecrease
        self.velocity = velocity
        self.fade = fade # boolean to say if value should fade

class Bullet(Entity):

    def __init__(self, collider, x, y, mass, dmg, kb, colour, time, id):
        super().__init__(collider, x, y, mass, colour)
        self.id = id # needed for enemies to have local invincibility when a hit a by a specific bullet but still be able to be hit by another also defines type
        self.time = time
        self.direction = np.array([0,0])
        self.relativePos = np.array([0,0])
        self.dmg = dmg
        self.kb = kb

class powerUP(Entity):

    #to keep concise and not blown out of proportions powerup generation code will be here

    def __init__(self, collider: CollisionObject, x, y, mass, colour, type): # they all have circle colliders and same size as circle
        super().__init__(collider, x, y, mass, colour)
        self.type = type
        self.time = 60*5

#region enemy time
class Enemy(Entity): #all enemies are squares i don't care about your opinion
    def __init__(self, x, y, width, height, mass, force, dmg, hp, kb, localInvincibility, AI, element, colour):
        super().__init__(CollisionRect(width,height), x, y, mass, colour)
        self.element = element
        self.dmg = dmg
        self.force = force
        self.hp = hp
        self.kb = kb # good ol knockback
        self.AI = AI
        self.direction = np.empty(2)
        self.localInvincibility = localInvincibility
        self.hits = {}

class DmgField(Entity):

    def __init__(self, x, y, width, height, mass ,direction, dmg, kb, colour):
        super().__init__(CollisionRect(width,height),x,y,mass,colour)
        self.direction = direction
        self.dmg = dmg
        self.kb = kb


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

#endregion classes

#region functions

#first function after 582 lines of code have been written
def circleToWall(o, w): #code is too fundamentally different for different shapes so had make separate functions, a bigger function could manage these if needed
    if CollisionObject.rectInCircle(w.physics.position[0], w.physics.position[1], w.collider,
                                    o.physics.position[0], o.physics.position[1],
                                    o.collider):
        # collision has occurred
        dy = (w.physics.position[1] + w.collider.height / 2) - o.physics.position[1]
        dx = (w.physics.position[0] + w.collider.width / 2) - o.physics.position[0]
        if abs(dy) / w.collider.height > abs(dx) / w.collider.width:
            counterForce = -physicsObject.findResultant(o.physics)[1]
            o.physics.addForce([0, counterForce])
            o.physics.velocity[1] = 0
            if dy > 0:
                o.physics.position[1] = w.physics.position[1] - (o.collider.r + 1)
            else:
                o.physics.position[1] = w.physics.position[1] + w.collider.height + (
                        o.collider.r + 1)
        else:
            counterForce = -physicsObject.findResultant(o.physics)[0]
            o.physics.addForce([counterForce, 0])
            o.physics.velocity[0] = 0
            if dx > 0:
                o.physics.position[0] = w.physics.position[0] - (o.collider.r + 1)
            else:
                o.physics.position[0] = w.physics.position[0] + w.collider.width + (
                        o.collider.r + 1)

def RectToWall(o, w): #code is too fundamentally different for different shapes so had make separate functions, a bigger function could manage these if needed
    if CollisionObject.rectInRect(w.physics.position[0], w.physics.position[1], w.collider, o.physics.position[0], o.physics.position[1], o.collider):
        # collision has occurred
        dy = (w.physics.position[1] + w.collider.height / 2) - (o.physics.position[1] + o.collider.height / 2)
        dx = (w.physics.position[0] + w.collider.width / 2) - (o.physics.position[0] + o.collider.width / 2)
        if abs(dy) / w.collider.height > abs(dx) / w.collider.width:

            counterForce = -physicsObject.findResultant(o.physics)[1]
            o.physics.addForce([0, counterForce])
            o.physics.velocity[1] = 0
            if dy > 0:
                o.physics.position[1] = w.physics.position[1] - (o.collider.height + 1)
            else:
                o.physics.position[1] = w.physics.position[1] + w.collider.height + 1
        else:
            counterForce = -physicsObject.findResultant(o.physics)[0]
            o.physics.addForce([counterForce, 0])
            o.physics.velocity[0] = 0
            if dx > 0:
                o.physics.position[0] = w.physics.position[0] - (o.collider.width + 1)
            else:
                o.physics.position[0] = w.physics.position[0] + w.collider.width + 1

def transparentColour(colour, alpha):
    return (colour[0], colour[1], colour[2], alpha)
#endregion

#region window setup
width = 1200
height = 800
window = pygame.display.set_mode((width, height))
surface = pygame.Surface((width,height), pygame.SRCALPHA)
pygame.display.set_caption('Circle FIGHTS back')
#endregion window setup

#region constants and initial variables that we want to define
#region colours       ( R , G , B , A ) the last one is a special value used for very specific things when needed
colours = {
    "black":          ( 0 , 0 , 0 ),
    "white":          (255,255,255),
    "grey":           (170,170,170),
    "red":            (255, 0 , 0 ),
    "green":          ( 0 ,255, 0 ),
    "blue":           ( 0 , 0 ,255),
    "dark red":       (122, 0 , 0 ),
    "dark green":     ( 0 , 74, 0 ),
    "wood":           (250,217,145),
    "orange":         (252,139, 73),
    "purple":         (102, 66,245),
    "yellow":         (255,200, 0 ),
    "wind":           (255,231,209),
    "flame":          (255, 90, 0 ),
    "electric":       (249,170, 0 ),
    "steel":          (224,229,229),
    "dark earth":     ( 46, 26, 0 ),
    "earth":          ( 92, 55, 0 ),
    "ice":            (181,255,254),
    "icePlatform":    (209,255,254)
}
#endregion colours


# region environment setup
bg_colour = colours["white"]
staticRenderObjects = [] # these are objects that'll never ever change there position except for scrollling purpose
staticRenderObjects.append(RenderRect(-3000, height/2, 6000, 20, colours["wood"]))
staticRenderObjects.append(RenderRect(width/2, -3000, 20, 6000, colours["wood"]))
walls = []
walls.append(Entity(CollisionRect(1000, 7500), 3100, -3300, 20, colours["black"])) # right
walls.append(Entity(CollisionRect(7500, 1000), -3300, -4100, 20, colours["black"]))  # up
walls.append(Entity(CollisionRect(1000, 7500), -4100, -3300, 20, colours["black"])) # left
walls.append(Entity(CollisionRect(7500, 1000), -3300, 3100, 20, colours["black"])) # down
dragFactor = 1 # the force counteracting on object so we can have terminal velocity(models stuff like friction and air resistance)
# endregion environment setup

# region Entities setup excluding player
entities = [] #
enemies = []
effects = []
powerUps = []
# endregion Entity setup


#region game stats
playerObject = Entity(CollisionCircle(20), width / 2, height / 2, 20, colours["red"])
playerForce = 5 #determines the speed of a player
playerDragFactor = 1

playerMaxHP = 10
playerHp = playerMaxHP

playerMaxStamina = 50
playerStamina = playerMaxStamina
dashStaminaConsumption = 10
staminaRegen = 0.1

meleeDmg = 1
meleeKB = 400
meleeSpeed = 2
meleeSize = 15
swingCD = 0.6
meleeLinger = 0.6

bulletConsumption = 5
bulletDmg = 1
bulletKB = 100
bulletSpeed = 10
bulletSize = 5
bulletCD = 0.01 #
bulletLinger = 10

homingConsumption = 30
homingCD = 1
homingDmg = 1
homingKB = meleeKB
homingSpeed = meleeSpeed
homingSize = 10
homingLinger = 10

playerProjectiles = []
bulletIDs = 0

score = 0

numOfEnemies = inputNumOfEnemies
wave = 0
maxEnemyForce = 10 # the variables here determine the difficulty and difficulty should typically get higher over time
minEnemyForce = 1
minEnemyKB = 200
maxEnemyKB = 250
minEnemyHp = 1
maxEnemyHp = 1
minEnemyDmg = 1
maxEnemyDmg = 1
enemySize = 40
bigEnemySize = 50
smallEnemySize = 20
enemySizeVariance = 5
enemyLocalInvincibility = 0.25
enemyTypes = {"sizes":False, "burster":False, "spiralIn":False, "Looker":False}

enemyProjectiles = []
enemyProjectileLimit = 500 #lower this for better performance
electricFields = [] # will be in transparent render objects
IceFields = []

wallLimit = 500

difficultySlider = inputdiffculty # how fast the game ramps up in difficulty the smaller the number the faster it ramps up
powerUpSlider = inputPowerSlider # how common power ups are
                            #insert [title] card
statuses = {"staminaRegen?":0, "invincible":0, "swingCD":0, "stunned":0, "dashing":0, "shootCD":0, "homingCD":0, "waveDisplay":0}  # gonna be a timer holding onto global cooldowns like if a player is stunned and can't move

#endregion game stats

#region UI
UIsize = 50
maxHpBar = RenderCircle(width-(10+UIsize),UIsize+10,UIsize,colours["dark red"])
hpBar = RenderCircle(width-(10+UIsize),UIsize+10,UIsize*(playerHp/playerMaxHP),colours["red"])
maxStaminaBar = RenderCircle(width-(10+UIsize),3*(UIsize+10),UIsize,colours["dark green"])
staminaBar = RenderCircle(width-(10+UIsize),3*(UIsize+10),UIsize*(playerStamina/playerMaxStamina),colours["green"])

scoreText = RenderText(10,10, 1200, UIsize, colours["purple"], int(1.5*UIsize), str(score))
gameOverText = RenderText(200,300, 1200, 3*UIsize, colours["red"], int(3*UIsize), "Game Over")
WaveText = RenderText(200,300, 1200, 3*UIsize, colours["purple"], int(2*UIsize), "Wave")

#endregion UI


clock = pygame.time.Clock()
FPS = 60
running = True


#endregion constants and initial variable that we want to define



#region main game loop
while running:

    #region input detection

    #is an input active detection(important for movement and autofire)
    keys = pygame.key.get_pressed()
    if statuses["stunned"] == 0:
        if keys[K_a]:
            playerObject.physics.addForce(np.array([-playerForce, 0]))
        if keys[K_d]:
            playerObject.physics.addForce(np.array([playerForce, 0]))
        if keys[K_s]:
            playerObject.physics.addForce(np.array([0, playerForce]))
        if keys[K_w]:
            playerObject.physics.addForce(np.array([0, -playerForce]))
        if keys[K_p]:
            playerStamina -= 2 * staminaRegen
    #has input state changed(important for buttons that only need to be pressed once like pressing menu)
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and playerStamina>0 and statuses["stunned"]==0:
                if keys[K_a] or keys[K_d] or keys[K_s] or keys[K_w]:
                    playerStamina -= dashStaminaConsumption
                    statuses["staminaRegen?"] = FPS*0.25
                    statuses["dashing"] = FPS * 0.25
                if keys[K_a]:
                    playerObject.physics.addForce(np.array([-playerForce*50, 0]))
                if keys[K_d]:
                    playerObject.physics.addForce(np.array([playerForce*50, 0]))
                if keys[K_s]:
                    playerObject.physics.addForce(np.array([0, 50*playerForce]))
                if keys[K_w]:
                    playerObject.physics.addForce(np.array([0, -playerForce*50]))
            if event.key == pygame.K_f and statuses["swingCD"] <= 0:
                playerProjectiles.append(Bullet(CollisionCircle(meleeSize), playerObject.physics.position[0], playerObject.physics.position[1], 20, meleeDmg, meleeKB,colours["orange"], meleeLinger*FPS, "m"+str(bulletIDs)))
                bulletIDs += 1
                if bulletIDs >= 100:
                    bulletIDs = 0
                statuses["swingCD"] = swingCD*FPS
                # now find the enemy with the shortest distance
                dy=99999999
                dx=99999999
                for i in enemies:
                    if((i.physics.position[0]-playerObject.physics.position[0])**2+(i.physics.position[1]-playerObject.physics.position[1])**2<(dy)**2+(dx)**2):
                        dy = (i.physics.position[1]+i.collider.height/2)-playerObject.physics.position[1]
                        dx = (i.physics.position[0]+i.collider.width/2)-playerObject.physics.position[0]
                # now normalise dy and dx
                magnitude = np.sqrt(dy**2 + dx**2)
                dy /= magnitude
                dx /= magnitude
                playerProjectiles[-1].direction = np.array([dx, dy])
            if event.key == pygame.K_e and statuses["shootCD"] <= 0 and playerStamina > 0:
                playerStamina -= bulletConsumption
                statuses["staminaRegen?"] = FPS * 0.25
                playerProjectiles.append(Bullet(CollisionCircle(bulletSize), playerObject.physics.position[0], playerObject.physics.position[1], 20, bulletDmg, bulletKB,colours["blue"], bulletLinger*FPS, "b"+str(bulletIDs)))
                bulletIDs += 1
                if bulletIDs >= 100:
                    bulletIDs = 0
                statuses["shootCD"] = bulletCD*FPS
                # now find the enemy with the shortest distance
                dy=99999999
                dx=99999999
                for i in enemies:
                    if((i.physics.position[0]-playerObject.physics.position[0])**2+(i.physics.position[1]-playerObject.physics.position[1])**2<(dy)**2+(dx)**2):
                        dy = (i.physics.position[1]+i.collider.height/2)-playerObject.physics.position[1]
                        dx = (i.physics.position[0]+i.collider.width/2)-playerObject.physics.position[0]
                # now normalise dy and dx
                magnitude = np.sqrt(dy**2 + dx**2)
                dy /= magnitude
                dx /= magnitude
                playerProjectiles[-1].direction = np.array([dx, dy])
            if event.key == pygame.K_q and statuses["homingCD"] <= 0 and playerStamina>20:
                playerStamina -= homingConsumption
                statuses["staminaRegen?"] = FPS * 1
                playerProjectiles.append(Bullet(CollisionCircle(homingSize), playerObject.physics.position[0], playerObject.physics.position[1], 20, homingDmg, homingKB,colours["yellow"], homingLinger*FPS, "h"+str(bulletIDs)))
                bulletIDs += 1
                if bulletIDs >= 100:
                    bulletIDs = 0
                statuses["homingCD"] = homingCD*FPS
                # now find the enemy with the shortest distance
                dy=99999999
                dx=99999999
                for i in enemies:
                    if((i.physics.position[0]-playerObject.physics.position[0])**2+(i.physics.position[1]-playerObject.physics.position[1])**2<(dy)**2+(dx)**2):
                        dy = (i.physics.position[1]+i.collider.height/2)-playerObject.physics.position[1]
                        dx = (i.physics.position[0]+i.collider.width/2)-playerObject.physics.position[0]
                # now normalise dy and dx
                magnitude = np.sqrt(dy**2 + dx**2)
                dy /= magnitude
                dx /= magnitude
                playerProjectiles[-1].direction = np.array([dx, dy])


        if event.type == pygame.QUIT:
            running = False
    #endregion input detection

    #region processing

    #region Wave management System
    if len(enemies) == 0: # this means a new wave should start
        wave += 1
        if wave % 2 == 1 and wave > 5:
            walls = []
            walls.append(Entity(CollisionRect(1000, 7500), 3100, -3300, 20, colours["black"]))  # right
            walls.append(Entity(CollisionRect(7500, 1000), -3300, -4100, 20, colours["black"]))  # up
            walls.append(Entity(CollisionRect(1000, 7500), -4100, -3300, 20, colours["black"]))  # left
            walls.append(Entity(CollisionRect(7500, 1000), -3300, 3100, 20, colours["black"]))  # down
            for w in range(200):
                walls.append(Entity(CollisionRect(random.randint(1, 300), random.randint(1, 300)), random.randint(-3000, 3000), random.randint(-3000, 3000), 1000, colours["black"]))
        WaveText.changeText("Wave " + str(wave))
        statuses["waveDisplay"] = FPS*2
        playerHp = playerMaxHP # restore hp
        enemyProjectiles = []
        iceFields = []
        #probability of base difficulty sliders going up we'll stick to 1 in 10 but that could be known as the difficulty slider nvm let's implement it
        if random.randint(1,difficultySlider)==1:
            maxEnemyForce += 2
            if random.randint(1,difficultySlider)==1:
                minEnemyForce += 2
        if random.randint(1,difficultySlider)==1:
            maxEnemyKB += 20
            if random.randint(1,difficultySlider)==1:
                minEnemyKB += 20
        if random.randint(1,difficultySlider*2)==1:
            maxEnemyHp += 1
            if random.randint(1,difficultySlider*2)==1:
                minEnemyHp += 1
        if random.randint(1,difficultySlider)==1:
            maxEnemyDmg += 1
            if random.randint(1,difficultySlider)==1:
                minEnemyDmg += 1
        elements = ["fire", "wind", "electric", "ice", "steel3", "earth", "null"]
        availableElements = []
        #custom element selector which could just use random.choice
        if wave>20: # every single element is deployed
            availableElements = [("fire",colours["red"]),("wind",colours["wind"]),("electric",colours["electric"]),("ice",colours["ice"]),("earth",colours["earth"]),("null",colours["grey"]), ("steel3",colours["steel"])]
        elif wave>15:
            for i in range(3):
                randElement = random.randint(1, 7)
                if randElement == 1:
                    availableElements.append(("fire", colours["red"]))
                elif randElement == 2:
                    availableElements.append(("wind", colours["wind"]))
                elif randElement == 3:
                    availableElements.append(("electric", colours["electric"]))
                elif randElement == 4:
                    availableElements.append(("ice", colours["ice"]))
                elif randElement == 5:
                    availableElements.append(("earth", colours["earth"]))
                elif randElement == 6:
                    availableElements.append(("steel3", colours["steel"]))
                else:
                    availableElements.append(("null", colours["grey"]))
        elif wave>10:
            for i in range(2):
                randElement = random.randint(1, 7)
                if randElement == 1:
                    availableElements.append(("fire", colours["red"]))
                elif randElement == 2:
                    availableElements.append(("wind", colours["wind"]))
                elif randElement == 3:
                    availableElements.append(("electric", colours["electric"]))
                elif randElement == 4:
                    availableElements.append(("ice", colours["ice"]))
                elif randElement == 5:
                    availableElements.append(("earth", colours["earth"]))
                elif randElement == 6:
                    availableElements.append(("steel3", colours["steel"]))
                else:
                    availableElements.append(("null", colours["grey"]))

        else:
            randElement = random.randint(1,7)
            if randElement==1:
                availableElements.append(("fire",colours["red"]))
            elif randElement==2:
                availableElements.append(("wind",colours["wind"]))
            elif randElement==3:
                availableElements.append(("electric",colours["electric"]))
            elif randElement==4:
                availableElements.append(("ice",colours["ice"]))
            elif randElement==5:
                availableElements.append(("earth",colours["earth"]))
            elif randElement==6:
                availableElements.append(("steel3",colours["steel"]))
            else:
                availableElements.append(("null", colours["grey"]))



        if(wave % 5==1):
            enemyTypes = {"sizes": False, "burster": False, "spiralIn": False, "Looker": False}
        if random.randint(1,3)==1:
            enemyTypes["spiralIn"] = True
        if random.randint(1,3)==1:
            enemyTypes["sizes"] = True
        if random.randint(1,3)==1:
            enemyTypes["burster"] = True
        if random.randint(1,3)==1:
            enemyTypes["Looker"] = True


        for i in range(numOfEnemies): # deploy new enemies
            AI = [Pursuer()]
            if enemyTypes["spiralIn"]:
                AI.append(SpiralIn(bool(random.getrandbits(1))))
            if enemyTypes["burster"]:
                AI.append(Burster(random.randint(1,5)*FPS, random.randint(100,150)))
            if enemyTypes["Looker"]:
                AI.append(Looker([random.randint(-700,700), random.randint(-400,400)]))
            if enemyTypes["sizes"]:
                randosize = random.randint(1,3)
                if randosize==1: # we going big
                    size = random.randint(bigEnemySize - enemySizeVariance, bigEnemySize + enemySizeVariance)
                    currentMass = 40
                    currentDmg = random.randint(minEnemyDmg, maxEnemyDmg)*2
                    currentKB = random.randint(minEnemyKB,maxEnemyKB)*2
                    currentHp  = 2*random.randint(minEnemyHp,maxEnemyHp)
                elif randosize==2: # we going small and shush IDE about grammer
                    size = random.randint(smallEnemySize - enemySizeVariance, smallEnemySize + enemySizeVariance)
                    currentMass = 10
                    currentDmg = random.randint(minEnemyDmg, maxEnemyDmg)*0.5
                    currentKB = random.randint(minEnemyKB, maxEnemyKB) * 0.5
                    currentHp  = random.randint(minEnemyHp,maxEnemyHp)*0.5
                else: # boo being normal
                    size = random.randint(enemySize - enemySizeVariance, enemySize + enemySizeVariance)
                    currentMass = 20
                    currentDmg = random.randint(minEnemyDmg, maxEnemyDmg)
                    currentKB = random.randint(minEnemyKB, maxEnemyKB)
                    currentHp  = random.randint(minEnemyHp,maxEnemyHp)
            else:
                random.randint(minEnemyDmg, maxEnemyDmg)
                size = random.randint(enemySize - enemySizeVariance, enemySize + enemySizeVariance)
                currentMass = 20
                currentKB = random.randint(minEnemyKB,maxEnemyKB)
                currentHp = 2 * random.randint(minEnemyHp, maxEnemyHp)
                currentDmg = random.randint(minEnemyDmg, maxEnemyDmg)
            currentElement = random.choice(availableElements)
            enemies.append(Enemy(random.randint(-2700,2700),random.randint(-2700,2700),size,size,currentMass,random.randint(minEnemyForce,maxEnemyForce),currentDmg,currentHp,currentKB,enemyLocalInvincibility*FPS, random.choice(AI), currentElement[0], currentElement[1]))
        numOfEnemies = int(np.ceil(numOfEnemies*1.1))
    #endregion

    #region enemy AI behaviour and adding forces
    for i in enemies:
        direction = i.AI.move(i.physics.position[0], i.physics.position[1], playerObject.physics.position[0], playerObject.physics.position[1])
        if direction[0] != 0 and direction[1] != 0:
            i.direction = direction
            i.physics.addForce(i.force*i.direction)
            i.direction /= np.linalg.norm(i.direction)
    #endregion

    #region physics manipulation and wall collision
    for i in enemies:
        i.physics.addForce(i.physics.velocity*-dragFactor)
        physicsObject.updatePhysics(i.physics)
    for i in powerUps:
        i.physics.addForce(i.physics.velocity*-dragFactor)
        physicsObject.updatePhysics(i.physics)
    playerObject.physics.addForce(playerObject.physics.velocity*-playerDragFactor) # add drag force
    # don't kill this code below
    for i in walls:
        if not keys[K_p]:
            circleToWall(playerObject, i) #no more chaotic looking code go refer to the function anyways all it does see the behaviour of an object trying to bash into a wall
        for j in enemies:
            if not(j.element == "wind" or j.element=="earth"):
                RectToWall(j, i)

    physicsObject.updatePhysics(playerObject.physics)
    #endregion physics manipulation


    #region enemy collision logic
    for i in enemies:
        if CollisionObject.rectInCircle(i.physics.position[0], i.physics.position[1], i.collider, playerObject.physics.position[0], playerObject.physics.position[1], playerObject.collider):
            if statuses["invincible"]==0:
                statuses["invincible"] = FPS*0.8
                playerHp -= i.dmg
                if i.element == "wind":
                    i.kb *= 1.5
                playerObject.physics.addForce(i.direction*i.kb)
    #endregion enemy collision logic

    #region enemy elemence management
    for i in enemies:
        if i.element == "fire":
            if(random.randint(1,360)==1): # how likely a fire attack can occur
                enemyProjectiles.append(Bullet(CollisionRect(max(i.collider.width/5,10),max(i.collider.width/5,10)), i.physics.position[0]+i.collider.width/2, i.physics.position[1]+i.collider.height/2, 20, i.dmg, i.kb/2, i.colour,10,"fire"))
                dy =   playerObject.physics.position[1] - (i.physics.position[1] + i.collider.height / 2)
                dx =   playerObject.physics.position[0] -(i.physics.position[0] + i.collider.width / 2)
                # now normalise dy and dx
                magnitude = np.sqrt(dy ** 2 + dx ** 2)
                dy /= magnitude
                dx /= magnitude
                enemyProjectiles[-1].direction = np.array([dx, dy])*random.randint(int(i.force/2),i.force)
        if i.element == "wind":
            if(random.randint(1,180)==1): # how likely a wind attack can occur
                enemyProjectiles.append(Bullet(CollisionRect(max(i.collider.width/5,10),max(i.collider.width/5,10)), i.physics.position[0]+i.collider.width/2, i.physics.position[1]+i.collider.height/2, 20, 0, i.kb*2, i.colour,5,"wind"))
                dy =   playerObject.physics.position[1] - (i.physics.position[1] + i.collider.height / 2)
                dx =   playerObject.physics.position[0] -(i.physics.position[0] + i.collider.width / 2)
                # now normalise dy and dx
                magnitude = np.sqrt(dy ** 2 + dx ** 2)
                dy /= magnitude
                dx /= magnitude
                enemyProjectiles[-1].direction = np.array([dx, dy])*random.randint(int(i.force/2),i.force)
        if i.element.startswith("steel"):
            if(random.randint(1,600)==1) and int(i.element[-1]) != 0: # how likely a steel summon occurs
                size = i.collider.width/2
                enemies.append(Enemy(i.physics.position[0], i.physics.position[1], size, size, i.physics.mass/2, i.force, i.dmg/2, i.hp, i.kb, enemyLocalInvincibility * FPS,i.AI, "steel0", colours["steel"]))
                enemies[-1].physics.addForce(np.array([random.uniform(-1,1),random.uniform(-1,1)*i.kb]))
                i.element = "steel"+str(int(i.element[-1])-1)

    #endregion
    #region specific elemence interactions
    electricEnemies = []
    windEnemies = []
    steelEnemies = []
    electricFields = []
    earthEnemies = []
    iceEnemies = []
    for i in enemies:
        if i.element.startswith("electric"):
            i.element = "electric"
            electricEnemies.append(i)
        elif i.element.startswith("wind"):
            windEnemies.append(i)
        elif i.element.startswith("steel"):
            steelEnemies.append(i)
        elif i.element == "earth":
            earthEnemies.append(i)
        elif i.element == "ice":
            iceEnemies.append(i)
    for i in electricEnemies:
        if i.element.endswith("charged"):
            continue
        # now find a compatible enemy with the shortest distance in a certain range
        dy = i.collider.height*5
        dx = i.collider.width*5
        latchEnemy = None
        for j in electricEnemies:
            if (i.physics.position[1] == j.physics.position[1] and i.physics.position[0] == j.physics.position[0]) or j.element.endswith("charged"):
                continue
            newdy = abs((i.physics.position[1] + i.collider.height/2) - (j.physics.position[1] + j.collider.height/2))
            newdx = abs((i.physics.position[0] + i.collider.width/2)  - (j.physics.position[0] + j.collider.width/2))
            if newdx**2+newdy**2 < dy**2+dx**2:
                dy = newdy
                dx = newdx
                latch = True
                latchCoords = [j.physics.position[0] + j.collider.width/2,j.physics.position[1] + j.collider.height/2]
                latchEnemy = j
            for j in windEnemies:
                if (i.physics.position[1] == j.physics.position[1] and i.physics.position[0] == j.physics.position[0]) or j.element.endswith("charged"):
                    continue
                newdy = abs((i.physics.position[1] + i.collider.height/2) - (j.physics.position[1] + j.collider.height/2))
                newdx = abs((i.physics.position[0] + i.collider.width/2)  - (j.physics.position[0] + j.collider.width/2))
                if newdx**2+newdy**2 < dy**2+dx**2:
                    dy = newdy
                    dx = newdx
                    latch = True
                    latchCoords = [j.physics.position[0] + j.collider.width/2,j.physics.position[1] + j.collider.height/2]
                    latchEnemy = j
            for j in steelEnemies:
                if (i.physics.position[1] == j.physics.position[1] and i.physics.position[0] == j.physics.position[0]) or j.element.endswith("charged"):
                    continue
                newdy = abs((i.physics.position[1] + i.collider.height/2) - (j.physics.position[1] + j.collider.height/2))
                newdx = abs((i.physics.position[0] + i.collider.width/2)  - (j.physics.position[0] + j.collider.width/2))
                if newdx**2+newdy**2 < dy**2+dx**2:
                    dy = newdy
                    dx = newdx
                    latch = True
                    latchCoords = [j.physics.position[0] + j.collider.width/2,j.physics.position[1] + j.collider.height/2]
                    latchEnemy = j
        if latchEnemy is not None:
            if latchEnemy.element == "wind":
                i.element = "electriccharged"
                pass
                #no field is generated if electric and wind are the closest 😈 but electric ignores the closest fire if an uncharged electric is close enough
            elif latchEnemy.element.startswith("steel"):
                i.element = "electriccharged"
                newDmg = (latchEnemy.dmg + i.dmg) / 2
                direction = np.add(i.direction, latchEnemy.direction) / 2
                newCoords = (min(i.physics.position[0] + i.collider.width / 2,latchEnemy.physics.position[0] + latchEnemy.collider.width / 2),min(i.physics.position[1] + i.collider.height / 2,latchEnemy.physics.position[1] + latchEnemy.collider.height / 2))
                electricFields.append(DmgField(newCoords[0], newCoords[1], dx, dy, 20, direction, newDmg, i.kb * 4, transparentColour(colours["electric"], 120)))

            elif latchEnemy.element == "electric":
                latchEnemy.element = "electriccharged"
                i.element = "electriccharged"
                newDmg = (latchEnemy.dmg + i.dmg)/2
                direction = np.add(i.direction , latchEnemy.direction) / 2
                newCoords = (min(i.physics.position[0] + i.collider.width/2,latchEnemy.physics.position[0] + latchEnemy.collider.width/2), min(i.physics.position[1] + i.collider.height/2,latchEnemy.physics.position[1] + latchEnemy.collider.height/2))
                electricFields.append(DmgField(newCoords[0], newCoords[1], dx, dy, 20, direction, newDmg, i.kb*4,transparentColour(colours["electric"], 120)))

    for i in earthEnemies:
        if not random.randint(1,600)==1: #the potential to make a wall
            continue
        dy = 400
        dx = 400
        latchEnemy = None
        for j in earthEnemies:
            if (i.physics.position[1] == j.physics.position[1] and i.physics.position[0] == j.physics.position[0]):
                continue
            newdy = abs(
                (i.physics.position[1] + i.collider.height / 2) - (j.physics.position[1] + j.collider.height / 2))
            newdx = abs((i.physics.position[0] + i.collider.width / 2) - (j.physics.position[0] + j.collider.width / 2))
            if newdx ** 2 + newdy ** 2 < dy ** 2 + dx ** 2:
                dy = newdy
                dx = newdx
                latch = True
                latchCoords = [j.physics.position[0] + j.collider.width / 2,
                               j.physics.position[1] + j.collider.height / 2]
                latchEnemy = j
        if latchEnemy != None:
            newCoords = (min(i.physics.position[0] + i.collider.width / 2,
                             latchEnemy.physics.position[0] + latchEnemy.collider.width / 2),
                         min(i.physics.position[1] + i.collider.height / 2,
                             latchEnemy.physics.position[1] + latchEnemy.collider.height / 2))
            walls.append(Entity(CollisionRect(dx,dy), newCoords[0], newCoords[1], i.physics.mass, colours["earth"]))
    for i in iceEnemies:
        if not random.randint(1,600)==1: #the potential to make a wall
            continue
        dy = 1000
        dx = 1000
        latchEnemy = None
        for j in iceEnemies:
            if (i.physics.position[1] == j.physics.position[1] and i.physics.position[0] == j.physics.position[0]):
                continue
            newdy = abs(
                (i.physics.position[1] + i.collider.height / 2) - (j.physics.position[1] + j.collider.height / 2))
            newdx = abs((i.physics.position[0] + i.collider.width / 2) - (j.physics.position[0] + j.collider.width / 2))
            if newdx ** 2 + newdy ** 2 < dy ** 2 + dx ** 2:
                dy = newdy
                dx = newdx
                latch = True
                latchCoords = [j.physics.position[0] + j.collider.width / 2,
                               j.physics.position[1] + j.collider.height / 2]
                latchEnemy = j
        if latchEnemy != None:
            newCoords = (min(i.physics.position[0] + i.collider.width / 2,
                             latchEnemy.physics.position[0] + latchEnemy.collider.width / 2),
                         min(i.physics.position[1] + i.collider.height / 2,
                             latchEnemy.physics.position[1] + latchEnemy.collider.height / 2))
            iceFields.append(Entity(CollisionRect(dx,dy), newCoords[0], newCoords[1], i.physics.mass, colours["icePlatform"]))

    #endregion


    #region bullet management deletion code should be separate to update code


    for i in playerProjectiles:
        i.time -= 1
        if i.id[0] == "m":
            if len(enemies) != 0:
                dy = 999999
                dx = 999999
                for j in enemies:
                    if ((j.physics.position[0] - playerObject.physics.position[0]) ** 2 + (j.physics.position[1] - playerObject.physics.position[1]) ** 2 < (dy) ** 2 + (dx) ** 2):
                        dy = (j.physics.position[1] + j.collider.height / 2) - playerObject.physics.position[1]
                        dx = (j.physics.position[0] + j.collider.width / 2) - playerObject.physics.position[0]
                # now normalise dy and dx
                magnitude = np.sqrt(dy ** 2 + dx ** 2)
                dy /= magnitude
                dx /= magnitude
                i.direction = np.array([dx, dy])
            i.relativePos = np.add(i.direction * meleeSpeed, i.relativePos)
            i.physics.position = np.add(i.relativePos, playerObject.physics.position)
        if i.id[0] == "h":
            if len(enemies) != 0:
                dy = 999999
                dx = 999999
                for j in enemies:
                    if ((j.physics.position[0] - i.physics.position[0]) ** 2 + (j.physics.position[1] - i.physics.position[1]) ** 2 < (dy) ** 2 + (dx) ** 2):
                        dy = (j.physics.position[1] + j.collider.height / 2) - i.physics.position[1]
                        dx = (j.physics.position[0] + j.collider.width / 2) - i.physics.position[0]
                # now normalise dy and dx
                magnitude = np.sqrt(dy ** 2 + dx ** 2)
                dy /= magnitude
                dx /= magnitude
                i.direction = np.array([dx, dy])
            i.physics.position = np.add(i.direction * homingSpeed, i.physics.position)
        if i.id[0] == "b":
            i.physics.position = np.add(i.direction * bulletSpeed, i.physics.position)

    for i in playerProjectiles[:]:
        if i.time <= 0:
            playerProjectiles.remove(i)

    newPlayerProjectiles = []
    for i in playerProjectiles[:]:
        remove = False
        if i.id[0] == "b" or i.id[0] == "h":
            for j in walls:
                if CollisionObject.rectInCircle(j.physics.position[0], j.physics.position[1], j.collider, i.physics.position[0], i.physics.position[1], i.collider):
                    remove = True
                    break
            # detect enemies
        for j in enemies[:]:
            if CollisionObject.rectInCircle(j.physics.position[0], j.physics.position[1], j.collider, i.physics.position[0], i.physics.position[1], i.collider):
                # enemy has been hit
                if not i.id in j.hits.keys():
                    if i.id[0] == "m":
                        j.hp -= i.dmg
                        j.hits[i.id] = j.localInvincibility * FPS
                        j.physics.addForce(i.direction*i.kb)
                    elif i.id[0] == "b" :
                        j.hp -= i.dmg
                        j.hits[i.id] = j.localInvincibility * FPS
                        j.physics.addForce(i.direction * i.kb)
                        remove = True
                    elif i.id[0] == "h" :
                        j.hp -= i.dmg
                        j.hits[i.id] = j.localInvincibility * FPS
                        j.physics.addForce(i.direction * i.kb)
                        remove = True
        if not remove:
            newPlayerProjectiles.append(i)
    playerProjectiles = newPlayerProjectiles

    for i in enemyProjectiles:
        i.physics.position = np.add(i.direction, i.physics.position)

    # fire and wind interaction
    wind_projectiles = []
    fire_projectiles = []
    great_projectiles = []
    basic_projectiles = []
    for p in enemyProjectiles:
        if p.id == "wind":
            wind_projectiles.append(p)
        elif p.id == "fire":
            fire_projectiles.append(p)
        else:
            basic_projectiles.append(p)

    for i in fire_projectiles: # electric and fire interaction
        for j in electricFields:
            if CollisionObject.rectInRect(i.physics.position[0], i.physics.position[1], i.collider, j.physics.position[0], j.physics.position[1], j.collider):
                i.direction *= 1.2 # we will let them projectiles accelerate in the field

    for i in wind_projectiles[:]:
        remove = False
        for j in fire_projectiles[:]:
            if CollisionObject.rectInRect(i.physics.position[0], i.physics.position[1], i.collider, j.physics.position[0], j.physics.position[1], j.collider):
                # fire and wind interaction when there bullets collide giga flame bullet is spawned in
                newDirection = np.add(i.direction, j.direction)
                newDirection /= 4
                great_projectiles.append(Bullet(CollisionRect(i.collider.width * 15, i.collider.height * 15), i.physics.position[0], i.physics.position[1],20, j.dmg * 2, i.kb * 2, colours["flame"], 10, "greatFlame"))
                great_projectiles[-1].direction = newDirection
                remove=True
                fire_projectiles.remove(j)
                break
        if remove:
            wind_projectiles.remove(i)
    enemyProjectiles = fire_projectiles + wind_projectiles + great_projectiles + basic_projectiles



    for i in enemyProjectiles[:]:
        remove = False
        if CollisionObject.rectInCircle(i.physics.position[0], i.physics.position[1], i.collider, playerObject.physics.position[0], playerObject.physics.position[1], playerObject.collider):
            if statuses["invincible"]==0:
                statuses["invincible"] = FPS*0.8
                playerHp -= i.dmg
                kbDirection = i.direction / max(1,np.linalg.norm(i.direction))
                playerObject.physics.addForce(kbDirection*i.kb)
                remove = True
        for j in walls:
            if CollisionObject.rectInRect(i.physics.position[0], i.physics.position[1], i.collider, j.physics.position[0], j.physics.position[1], j.collider):
                remove = True
        if i.id != "greatFlame":
            for j in playerProjectiles:
                if j.id[0] == "m" and CollisionObject.rectInCircle(i.physics.position[0], i.physics.position[1], i.collider, j.physics.position[0], j.physics.position[1], j.collider):
                    remove = True
        if remove:
            enemyProjectiles.remove(i)

    # curb enemy projectile amount and wall amount(so player don't get stuck somewhere)
    if len(enemyProjectiles) >= enemyProjectileLimit:
        for i in range(len(enemyProjectiles)-enemyProjectileLimit):
            del enemyProjectiles[0]
    if len(walls) >= wallLimit:
        for i in range(len(walls)-wallLimit):
            del walls[4]

    #endregion bullet management

    #field management, psst electric enemies are the only ones that have this property..... this ain't true anymore ice also have fields
    for i in electricFields:
        if CollisionObject.rectInCircle(i.physics.position[0], i.physics.position[1], i.collider, playerObject.physics.position[0], playerObject.physics.position[1], playerObject.collider):
            if statuses["invincible"]==0:
                statuses["invincible"] = FPS*0.8
                statuses["stunned"] = FPS*1.6
                playerHp -= i.dmg
                playerObject.physics.addForce(i.direction*i.kb)

    playerDragFactor = 1
    for i in iceFields:
        if CollisionObject.rectInCircle(i.physics.position[0], i.physics.position[1], i.collider, playerObject.physics.position[0], playerObject.physics.position[1], playerObject.collider):
            playerDragFactor = 0

    # enemy management
    for i in enemies[:]:
        if i.hp <= 0:
            # The enemy has died also this will be only spot to customise death effects
            numOfEffects = random.randint(3, 10)
            for e in range(numOfEffects):
                randSize = random.randint(1, 10)
                effects.append(Effect(CollisionRect(randSize, randSize), i.physics.position[0], i.physics.position[1], 20, i.colour, FPS * random.uniform(0.1, 0.5), 1,[random.uniform(-5, 5), random.uniform(-5, 5)], True))

            #generate a powerup if can happen
            if random.randint(1,powerUpSlider)==1:
                Atype = random.choice([("homing",colours["yellow"]), ("bullet",colours["blue"]), ("melee",colours["orange"]), ("stamina",colours["green"]), ("health",colours["red"])])
                powerUps.append(powerUP(CollisionCircle(20),i.physics.position[0], i.physics.position[1], 20, Atype[1], Atype[0]))
                powerUps[-1].physics.addForce(np.array([random.uniform(-1,1),random.uniform(-1,1)])*200)


            enemies.remove(i)
            score += 10
        for k in i.hits.copy():
            i.hits[k] -= 1
            if i.hits[k] <= 0:
                del i.hits[k]


    # powerup management and two seperate loops cuase i don't wanna deal with double deletetion
    for i in powerUps[:]:
        if CollisionObject.circleInCircle(i.physics.position[0], i.physics.position[1], i.collider, playerObject.physics.position[0], playerObject.physics.position[1], playerObject.collider):
            # the objects have collided
            for a in range(random.randint(1,10)):
                randSize = random.randint(1, 5)
                effects.append(Effect(CollisionCircle(randSize), i.physics.position[0], i.physics.position[1], 20, i.colour,FPS * random.uniform(0.1, 0.5), 1, [random.uniform(-5, 5), random.uniform(-5, 5)], True))
            #apply the effect the powerup needs to dish out
            if i.type=="health":
                if random.randint(1,2)==1:
                    playerMaxHP += 2
                else:
                    playerForce += 0.5
                playerHp = playerMaxHP
            if i.type == "stamina":
                if random.randint(1,2)==1:
                    playerMaxStamina += 20
                else:
                    staminaRegen += 0.01
                playerStamina = playerMaxStamina
            if i.type == "melee":
                randUpgrade = random.randint(1,10)
                if  1 <= randUpgrade <= 3:
                    meleeDmg += 1
                elif 4 <=  randUpgrade <= 6:
                    meleeSpeed += 0.5
                elif 10 <= randUpgrade <= 10:
                    if swingCD <= 0.11:
                        meleeDmg += 1
                        meleeSpeed += 0.5
                        meleeKB += 40
                        playerStamina = -1
                    else:
                        swingCD -= 0.1
                        meleeLinger -= 0.1
                elif 7 <= randUpgrade <= 9:
                    meleeKB += 40
            if i.type == "bullet":
                randUpgrade = random.randint(1,9)
                if  1 <= randUpgrade <= 3:
                    bulletDmg += 1
                elif 4 <=  randUpgrade <= 6:
                    bulletSpeed += 2
                elif 7 <= randUpgrade <= 9:
                    bulletKB += 10
            if i.type == "homing":
                randUpgrade = random.randint(1,9)
                if  1 <= randUpgrade <= 3:
                    homingDmg += 1
                elif 4 <=  randUpgrade <= 6:
                    homingSpeed +=0.5
                elif 7 <= randUpgrade <= 9:
                    homingKB += 40
            powerUps.remove(i)

    for i in powerUps[:]:
        i.time -= 1
        if i.time < 0:
            powerUps.remove(i)

    #region effect processing
    for i in effects[:]:
        i.time -= i.timeDecrease
        if i.fade:
            i.colour = transparentColour((i.colour[0],i.colour[1],i.colour[2]),(i.time/i.totalTime)*255)
        i.physics.position[0] += i.velocity[0]
        i.physics.position[1] += i.velocity[1]
        if i.time <= 0:
            effects.remove(i)

    #endregion effect processing

    #region game processing
    if playerStamina < 0:
        playerStamina=0
        statuses["staminaRegen?"] = FPS*3

    if playerStamina < playerMaxStamina and statuses["staminaRegen?"]==0:
        playerStamina += staminaRegen

    if statuses["dashing"]!=0:
        if statuses["dashing"]%3 == 0:
            effects.append(Effect(CollisionCircle(playerObject.collider.r),playerObject.physics.position[0],playerObject.physics.position[1],20,transparentColour(colours["red"],120),10,1,(0,0),True))

    if playerHp <= 0:
        running = False

    for k in statuses:
        if statuses[k]>0:
            statuses[k] -= 1
    #endregion

    #region update UI elements
    staminaBar.r = UIsize*playerStamina/playerMaxStamina
    hpBar.r = UIsize*playerHp/playerMaxHP
    scoreText.changeText(str(score))
    #endregion update UI elements
    #endregion processing

    #region Rendering Section
    """note always draw the background first then move your way to the foreground"""
    # the list below contains current objects we want to draw into the scene
    renderObjects = []
    transparentRenderObjects = []
    #if someone knows how to mass add lists let me know cause uhh yeah
    for i in staticRenderObjects: # strange bug happened that causes some weird things to occur so need to loop and add them
        RenderObject.scroll(i, playerObject.physics.position[0]-(width/2), playerObject.physics.position[1]-(height/2))
        renderObjects.append(i)
    for i in iceFields:
        j = i.returnRender()
        RenderObject.scroll(j, playerObject.physics.position[0] - (width / 2), playerObject.physics.position[1] - (height / 2))
        renderObjects.append(j)
    for i in walls:
        j = i.returnRender()
        RenderObject.scroll(j, playerObject.physics.position[0] - (width / 2),playerObject.physics.position[1] - (height / 2))
        renderObjects.append(j)
    for i in enemies:
        j = i.returnRender() # I love this method
        RenderObject.scroll(j, playerObject.physics.position[0] - (width / 2),playerObject.physics.position[1] - (height / 2))
        renderObjects.append(j)
    for i in playerProjectiles:
        j = i.returnRender()  # I love this method
        RenderObject.scroll(j, playerObject.physics.position[0] - (width / 2),playerObject.physics.position[1] - (height / 2))
        renderObjects.append(j)
    for i in enemyProjectiles:
        j = i.returnRender()  # I love this method
        RenderObject.scroll(j, playerObject.physics.position[0] - (width / 2),playerObject.physics.position[1] - (height / 2))
        renderObjects.append(j)
    for i in electricFields:
        j = i.returnRender() # I love this method
        RenderObject.scroll(j, playerObject.physics.position[0] - (width / 2), playerObject.physics.position[1] - (height / 2))
        transparentRenderObjects.append(j)
    for i in powerUps:
        j = i.returnRender()  # I love this method
        RenderObject.scroll(j, playerObject.physics.position[0] - (width / 2),
        playerObject.physics.position[1] - (height / 2))
        renderObjects.append(j)
    if statuses["stunned"]!=0: # probably not the right place to implement this but it's a visual issue
        offsetX = random.randint(-3,3)
        offsetY = random.randint(-3,3)
    else:
        offsetX = 0
        offsetY = 0
    renderObjects.append(RenderCircle((width/2)+offsetX, (height/2)+offsetY, 20, colours["red"]))
    for i in effects:
        j = i.returnRender()  # I love this method
        RenderObject.scroll(j, playerObject.physics.position[0] - (width / 2),playerObject.physics.position[1] - (height / 2))
        transparentRenderObjects.append(j)
     # our goofy player sprite
    transparentRenderObjects.append(maxHpBar)
    transparentRenderObjects.append(hpBar)
    transparentRenderObjects.append(maxStaminaBar)
    transparentRenderObjects.append(staminaBar)
    transparentRenderObjects.append((scoreText))
    if statuses["waveDisplay"] != 0:
        transparentRenderObjects.append(WaveText)
    window.fill(bg_colour)
    surface.fill((0,0,0,0))
    RenderObject.render(window, renderObjects)
    RenderObject.render(surface, transparentRenderObjects)
    window.blit(surface, (0,0))
    pygame.display.flip()
    clock.tick(FPS)
    #endregion Rendering Section
#endregion main game loop

#region endgame aftermath
renderObjects.append(gameOverText)
RenderObject.render(window, renderObjects)
pygame.display.flip()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


#endregion endgame afterx
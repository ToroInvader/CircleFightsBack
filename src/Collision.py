from fontTools.misc.bezierTools import epsilon

from ECS import *
from SpatialPartitioning import *
import Vector


#gosh this is gonna be real hard to clean up and root out the numpy system as well

#region collision component classes hold information about the shape of an object that's it they don't have access to position
# also handles collision
class CollisionComponent(Component):

    def __init__(self, shape, tag="default", mask=None):
        super().__init__("collision")
        if mask is None:
            mask = ["default"]
        self.shape = shape
        self.tag = tag
        self.mask = mask

class CollisionCircle(CollisionComponent):

    def __init__(self, r, tag="default", mask=None):
        super().__init__("circle", tag, mask)
        self.r = r

class CollisionRect(CollisionComponent):
    def __init__(self, width, height, tag="default", mask=None):
        super().__init__("rect", tag, mask)
        self.width = width
        self.height = height

class CollisionPolygon(CollisionComponent):

    def __init__(self, points, tag="default", mask=None): #input points in this format
        super().__init__("polygon", tag, mask)
        self.points = Vector.forceCounterClockwise(points)
        self.normals = []
        for i in range(len(self.points)):
            A = i
            B = (i+1) % len(self.points)
            AB = Vector.Subtract(self.points[B], self.points[A])
            normal = Vector.Normal(Vector.Unit(AB))
            self.normals.append(normal)



#endregion collision object classes
#region system time

class CollisionSystem:

    def __init__(self, cellSize=100):
        self.last_frame_collisions = set()
        self.this_frame_collisions = set()
        self.grid = SpatialHashGrid(cellSize)

    def tick(self, ecs : ECS): # note this method returns the eids that received a collision as a pair
        self.last_frame_collisions = self.this_frame_collisions
        self.this_frame_collisions = set()
        self.grid.clear()
        #insert all collidable entities into spatial grid
        for id in ecs.query("collision", "position"):
            collider = ecs.get_component(id, "collision")
            position = ecs.get_component(id, "position")
            box = self.getBoundingBox(position, collider)
            self.grid.insert(id, box[0], box[1], box[2], box[3])
        for id1 in ecs.query("collision", "position"):
            collider1 = ecs.get_component(id1, "collision")
            position1 = ecs.get_component(id1, "position")
            box = self.getBoundingBox(position1, collider1)
            candidates = self.grid.query_neighbours(box[0], box[1], box[2], box[3])
            for id2 in candidates:
                if id1==id2:
                    continue
                collider2 = ecs.get_component(id2, "collision")
                position2 = ecs.get_component(id2, "position")
                if not collider2.tag in collider1.mask:
                    continue
                #alright test the collision
                if self.collide(collider1, position1, collider2, position2):
                    self.this_frame_collisions.add((id1,id2))
        #this might be expensive constantly building this dictionary
        events = {"enter": self.this_frame_collisions - self.last_frame_collisions,
                  "stay": self.this_frame_collisions & self.last_frame_collisions,
                  "exit": self.last_frame_collisions - self.this_frame_collisions}
        return events


    def collide(self, collider1, position1, collider2, position2):
                if collider1.shape == "circle" and collider2.shape == "circle":
                    return self.circleInCircle(position1.position[0], position1.position[1], collider1, position2.position[0], position2.position[1], collider2)
                elif collider1.shape == "polygon" and collider2.shape == "polygon":
                    return self.polygonInPolygon(position1.position[0], position1.position[1], collider1, position2.position[0], position2.position[1], collider2)
                elif collider1.shape == "rect" and collider2.shape == "rect":
                    return self.rectInRect(position1.position[0], position1.position[1], collider1, position2.position[0], position2.position[1],collider2)
                elif collider1.shape == "circle" and collider2.shape == "polygon":
                    return self.PolygonToCircle(position2.position[0], position2.position[1], collider2, position1.position[0], position1.position[1],collider1)
                elif collider1.shape == "polygon" and collider2.shape == "circle":
                    return self.PolygonToCircle(position1.position[0], position1.position[1], collider1, position2.position[0], position2.position[1],collider2)
                elif collider1.shape == "circle" and collider2.shape == "rect":
                    return self.rectInCircle(position2.position[0], position2.position[1], collider2, position1.position[0], position1.position[1],collider1)
                elif collider1.shape == "rect" and collider2.shape == "circle":
                    return self.rectInCircle(position1.position[0], position1.position[1], collider1, position2.position[0], position2.position[1],collider2)
                elif collider1.shape == "polygon" and collider2.shape == "rect":
                    return self.rectInPolygon(position2.position[0], position2.position[1], collider2,position1.position[0], position1.position[1], collider1)
                elif collider1.shape == "rect" and collider2.shape == "polygon":
                    return self.rectInPolygon(position1.position[0], position1.position[1], collider1,position2.position[0], position2.position[1], collider2)

                #make sure to include rect and polygon interacting with each other

    def getBoundingBox(self, position ,collider): #returns [x, y, width, height]
        if collider.shape == "rect":
            return [position.position[0],position.position[1], collider.width, collider.height]
        elif collider.shape == "circle":
            return [position.position[0],position.position[1],2*collider.r, 2*collider.r]
        elif collider.shape == "polygon":
            xs =  [point[0] for point in collider.points]
            ys =  [point[1] for point in collider.points]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            width = max_x-min_x
            height = max_y-min_y
            center_x = position.position[0] + ((min_x + max_x) / 2)
            center_y = position.position[1] + ((min_y + max_y) / 2)
            return [center_x, center_y, width, height]
        else:
            print("you what")


    def pointInCircle(self, x, y, c, cx, cy):
        euclideanDistance = math.sqrt( ((x-cx)**2) + ((y-cy)**2) )
        return euclideanDistance <= c.r

    def pointInRect(self, x, y, c, cx, cy): #c is the collision object with its position as cx and cy
        left = cx-(c.width/2)
        top =  cy - (c.height / 2)
        return ((left <= x <= left + c.width) and
                (top <= y <= top + c.height))

    def pointInPolygon(self, x, y, c, cx, cy):
        # Shift polygon points by (cx, cy)
        polyPoints = [[px + cx, py + cy] for px, py in c.points]
        sign = None
        for i in range(len(polyPoints)):
            A = polyPoints[i]
            B = polyPoints[(i + 1) % len(polyPoints)]
            ABx = B[0] - A[0]
            ABy = B[1] - A[1]
            APx = x - A[0]
            APy = y - A[1]
            cross = ABx * APy - ABy * APx
            if cross != 0:
                current_sign = cross > 0
                if sign is None:
                    sign = current_sign
                elif sign != current_sign:
                    return False
        return True


    def linesIntersect(self, A, B, C, D): #chatgpt made this
        # checks if line AB and line CD intersect
        return (Vector.ccw(A, C, D) != Vector.ccw(B, C, D)) and (Vector.ccw(A, B, C) != Vector.ccw(A, B, D))

    def polygonInPolygon(self, t1px, t1py, t1c, t2px, t2py, t2c): # utilise Separating Axis Theorem if push comes to shove make the code pure python to optimise the code
        # grab points for t1 and t2
        points1 = []
        for point in t1c.points:
            points1.append([point[0]+t1px,point[1]+t1py])
        points2 = []
        for point in t2c.points:
            points2.append([point[0] + t2px, point[1] + t2py])
        # determine unit vectors of separating axes(the nominal vector of each side)
        separatingAxes = t1c.normals + t2c.normals
        # determine the scores(which is length of the vector projected onto the separating axes)
        # of all points for each separating axis
        EPSILON = 1e-6
        for axis in separatingAxes:
            values1 = []
            values2 = []
            for point in points1:
                values1.append(Vector.Dot(point, axis))
            for point in points2:
                values2.append(Vector.Dot(point, axis))
            # now check if the max and min compare well if not instantly return false
            t1Max = max(values1)
            t1Min = min(values1)
            t2Max = max(values2)
            t2Min = min(values2)
            if t1Max <= t2Min-epsilon or t2Max <= t1Min-epsilon:
                return False
        return True
    def PolygonToCircle(self, tpx, tpy, tc, spx, spy, sc):  # t:polygon, s:circle, p:position, c:collider
        points = [[p[0] + tpx, p[1] + tpy] for p in tc.points]
        n = len(points)
        for i in range(n): #repeats for every polygon side
            A = points[i]
            B = points[(i+1)%n]
            AB = Vector.Subtract(B, A)
            AC = Vector.Subtract([spx, spy], A)
            t = max(0, min(1, Vector.Dot(AB, AC) / (Vector.Magnitude(AB) ** 2))) #I don't think i'll remember how to do this later on but it makes sense
            closest = Vector.Add(A, Vector.scalarMult(t, AB))
            delta = Vector.Subtract(closest, [spx, spy])
            if Vector.Magnitude(delta) < sc.r:
                return True
        if self.pointInPolygon(spx, spy, tc, tpx, tpy):
            return True
        return False
    #make sure to adjust this to polygonToRect
    def rectInPolygon(self, tpx, tpy, tc, spx, spy, sc): #t:triangle, s:square, p:position, c:collider

        #Convert Rect into polygon form and work from there
        rect_points = [
            [-tc.width / 2, -tc.height / 2], # top left
            [-tc.width / 2, tc.height / 2], # bottom left
            [tc.width / 2, tc.height / 2], # bottom right
            [tc.width / 2, -tc.height / 2], # top right
        ]
        return self.polygonInPolygon(spx,spy,sc,tpx,tpy,CollisionPolygon(rect_points))


    def rectInRect(self, s1px, s1py, s1c, s2px, s2py, s2c): # numbers used to differentiate the colliders
        # keep above code for poking apparently and redundancy ig
        left1 = s1px - s1c.width / 2
        right1 = s1px + s1c.width / 2
        top1 = s1py - s1c.height / 2
        bottom1 = s1py + s1c.height / 2

        left2 = s2px - s2c.width / 2
        right2 = s2px + s2c.width / 2
        top2 = s2py - s2c.height / 2
        bottom2 = (s2py + s2c.height / 2)

        return (left1 <= right2 and
                right1 >= left2 and
                top1 <= bottom2 and
                bottom1 >= top2)

    def rectInCircle(self, s1px, s1py, s1c, s2px, s2py, s2c):  # numbers used to differentiate the colliders
        dy = 0
        dx = 0
        left = s1px - (s1c.width / 2)
        top = s1py -(s1c.height / 2)
        if top <= s2py <= top+s1c.height and left <= s2px <= left+s1c.width:
            return True # this means the circle is inside the rect
        if top <= s2py <= top+s1c.height:
            dx = min(abs(s2px - left), abs(s2px - (left+s1c.width))) #this code might be confusing but it's trying to find the vertical side closer to the circle
            return dy ** 2 + dx ** 2 <= s2c.r ** 2
        elif left <= s2px <= left+s1c.width:
            dy = min(abs(s2py - top), abs(s2py - (top+s1c.height))) # same but horizontal
            return dy ** 2 + dx ** 2 <= s2c.r ** 2
        else:
            dx = min(abs(s2px - left), abs(s2px - (left+s1c.width)))
            dy = min(abs(s2py - top), abs(s2py - (top+s1c.height)))
            return dy ** 2 + dx ** 2 <= s2c.r ** 2 # see if the closest point found is in the circle via Euclidean distance


    def circleInCircle(self, s1px, s1py, s1c, s2px, s2py, s2c): # most interesting one doesn't rely on point information and least expensive to compute
        euclideanDistance = math.sqrt(((s1px - s2px) ** 2) + ((s1py - s2py) ** 2))
        return euclideanDistance < (s1c.r + s2c.r)
#endregion
from Physics import  *
from Collision import *
import Vector


class Material(Component): # for static and dynamic objects which behave differently
    def __init__(self, restitution):
        super().__init__("material")
        self.restitution = restitution

class RigidBody(Component): # for dynamic collision resolvement

    def __init__(self,):
        super().__init__("rigidbody")

class StaticBody(Component): # for when a dynamic object collides into the static object

    def __init__(self):
        super().__init__("staticbody")

class CollisionResolvementSystem:

    def tick(self, ecs: ECS, events):
        rigidTracker = set()
        for event in events["stay"] | events["enter"]:
            body1 = event[0]
            body2 = event[1]
            if ecs.has_component(body1, "rigidbody") and ecs.has_component(body2, "rigidbody"):
                pair = (body2, body1)
                if pair in rigidTracker: # prevent duplicate interactions since it's a symmetric interaction(both objects are the same)
                    continue
                self.resolveRigidToRigid(ecs, body1, body2)
                rigidTracker.add(pair)
        for event in events["stay"] | events["enter"]:
            body1 = event[0]
            body2 = event[1]
            if ecs.has_component(body1, "rigidbody") and ecs.has_component(body2, "staticbody"):
                self.resolveRigidToStatic(ecs, body1, body2)

    def resolveRigidToStatic(self, ecs: ECS, rigidID, staticID):
        #first figure out the minimum transition vector by looking at collision and position information
        rigidPos = ecs.get_component(rigidID, "position")
        rigidVel = ecs.get_component(rigidID, "velocity")
        rigidColl = ecs.get_component(rigidID, "collision")
        rigidPhysics= ecs.get_component(rigidID, "physics")
        staticPos = ecs.get_component(staticID, "position")
        staticColl = ecs.get_component(staticID, "collision")
        mtv = self.findMTV(rigidColl, rigidPos, staticColl, staticPos) # the mtv should be from static to rigid
        #now push rigid out
        rigidPos.position = Vector.Add(rigidPos.position, mtv)
        #now add the impulse
        removeVel = Vector.scalarMult(Vector.Dot(Vector.Unit(mtv), rigidVel.velocity), Vector.Unit(mtv))
        impulse = Vector.scalarMult(-rigidPhysics.mass, removeVel)
        rigidPhysics.forces.append(impulse)

    def resolveRigidToRigid(self, ecs: ECS, id1, id2):
        #first figure out the minimum transition vector by looking at collision and position information
        pos1 = ecs.get_component(id1, "position")
        vel1 = ecs.get_component(id1, "velocity")
        coll1 = ecs.get_component(id1, "collision")
        physics1 = ecs.get_component(id1, "physics")
        material1 = ecs.get_component(id1, "material")
        pos2 = ecs.get_component(id2, "position")
        vel2 = ecs.get_component(id2, "velocity")
        coll2 = ecs.get_component(id2, "collision")
        physics2= ecs.get_component(id2, "physics")
        material2 = ecs.get_component(id2, "material")
        mtv = self.findMTV(coll1, pos1, coll2, pos2) # the mtv should be from rigid2 to rigid1
        #now push the rigids out of each other
        # allow small slop
        slop = 0
        correctionPercent = 1
        mtvMag = Vector.Magnitude(mtv)
        if mtvMag > slop:
            correction = Vector.scalarMult((mtvMag - slop) * correctionPercent, Vector.Unit(mtv))
            pos1.position = Vector.Add(pos1.position, Vector.scalarMult(0.5, correction))
            pos2.position = Vector.Add(pos2.position, Vector.scalarMult(-0.5, correction))
        #now add the impulse and assume all the kinetic energy is conserved(no clue what that's gonna do)
        #unit vector in that direction
        normal = Vector.Unit(mtv)
        relVel = Vector.Subtract(vel1.velocity, vel2.velocity)
        relVel = Vector.Dot(relVel, normal)
        e = (material1.restitution + material2.restitution) / 2
        misc = -(1+e)/((1/physics1.mass)+(1/physics2.mass)) # this is just formulaic calculations
        impulse = Vector.scalarMult(misc * relVel, normal)
        physics1.forces.append(impulse)
        physics2.forces.append(Vector.scalarMult(-1, impulse)) # apply in the other direction for rigidbody 2


    def findMTV(self, collider1, position1, collider2, position2): #note mtv should always go from 2nd object to first object
        if collider1.shape == "circle" and collider2.shape == "circle":
            return self.findCircleToCircle(position1.position[0], position1.position[1], collider1, position2.position[0],position2.position[1], collider2)
        elif collider1.shape == "polygon" and collider2.shape == "polygon":
            return self.findPolygonToPolygon(position1.position[0], position1.position[1], collider1, position2.position[0],position2.position[1], collider2)
        elif collider1.shape == "rect" and collider2.shape == "rect":
            return self.findRectToRect(position1.position[0], position1.position[1], collider1, position2.position[0],position2.position[1], collider2)
        elif collider1.shape == "polygon" and collider2.shape == "circle":
            mtv = self.findCircleToPolygon(position2.position[0], position2.position[1], collider2, position1.position[0],position1.position[1], collider1)
            mtv = Vector.scalarMult(-1, mtv)
            return mtv
        elif collider1.shape == "circle" and collider2.shape == "polygon":
            return self.findCircleToPolygon(position1.position[0], position1.position[1], collider1, position2.position[0],position2.position[1], collider2)
        elif collider1.shape == "rect" and collider2.shape == "circle":
            mtv =  self.findCircleToRect(position2.position[0], position2.position[1], collider2, position1.position[0],position1.position[1], collider1)
            mtv = Vector.scalarMult(-1, mtv)
            return mtv
        elif collider1.shape == "circle" and collider2.shape == "rect":
            return self.findCircleToRect(position1.position[0], position1.position[1], collider1, position2.position[0],position2.position[1], collider2)
        elif collider1.shape == "polygon" and collider2.shape == "rect":
            return self.findRectToPolygon(position2.position[0], position2.position[1], collider2, position1.position[0],position1.position[1], collider1)
        elif collider1.shape == "rect" and collider2.shape == "polygon":
            mtv = self.findRectToPolygon(position1.position[0], position1.position[1], collider1, position2.position[0],position2.position[1], collider2)
            mtv = Vector.scalarMult(-1, mtv)
            return mtv

    def findCircleToCircle(self,  s1px, s1py, s1c, s2px, s2py, s2c):
        S2toS1 = Vector.Subtract([s1px, s1py], [s2px, s2py])
        mtv = Vector.Unit(S2toS1)
        distance = Vector.Magnitude(S2toS1)
        depth = s1c.r + s2c.r - distance
        return Vector.scalarMult(depth, mtv)

    def findCircleToRect(self, s1px, s1py, s1c, s2px, s2py, s2c):
        #also we hand down know they're touching
        left = s2px - (s2c.width / 2)
        top = s2py -(s2c.height / 2)
        closestX = max(left, min(s1px, left+s2c.width))#finds the closest point on the circle when it's outside
        closestY = max(top, min(s1py, top+s2c.height))
        BA = Vector.Subtract([s1px, s1py], [closestX, closestY])
        dist = Vector.Magnitude(BA)
        if dist == 0: # if true we know center is inside the square
            dx = min(abs(s1px - left), abs(left + s2c.width - s1px))
            dy = min(abs(s1py - top), abs(top+s2c.height - s1py))
            if dx < dy:# push on shallow axis
                mtv = [1, 0] if s1px - s2px > 0 else [-1, 0]
                depth = dx + s1c.r
            else:
                mtv = [0, 1] if s1py - s2py > 0 else [0, -1]
                depth = dy + s1c.r
        else: # outside the square
            mtv = Vector.Unit(BA)
            depth = s1c.r - dist
        return Vector.scalarMult(depth, mtv)


    def findCircleToPolygon(self, spx, spy, sc, tpx, tpy, tc):  # t:polygon, s:circle, p:position, c:collider
        points = [[p[0] + tpx, p[1] + tpy] for p in tc.points]
        n = len(points)
        for i in range(n): #repeats for every polygon side
            A = points[i]
            B = points[(i+1)%n]
            AB = Vector.Subtract(B, A)
            AC = Vector.Subtract([spx, spy], A)
            t = max(0, min(1, Vector.Dot(AB, AC) / (Vector.Magnitude(AB) ** 2))) #I don't think i'll remember how to do this later on but it makes sense
            closest = Vector.Add(A, Vector.scalarMult(t, AB))
            delta = Vector.Subtract([spx, spy], closest)
            if Vector.Magnitude(delta) < sc.r:
                #delta should be our mtv
                mtv = Vector.Unit(delta)
                depth = sc.r - Vector.Magnitude(delta)
                return Vector.scalarMult(depth, mtv)
        return [0,0]

    def findPolygonToPolygon(self, t1px, t1py, t1c, t2px, t2py, t2c): # utilise Separating Axis Theorem if push comes to shove make the code pure python to optimise the code
        # grab points for t1 and t2
        points1 = []
        for point in t1c.points:
            points1.append([point[0]+t1px,point[1]+t1py])
        points2 = []
        for point in t2c.points:
            points2.append([point[0] + t2px, point[1] + t2py])
        # determine unit vectors of separating axes(the nominal vector of each side)
        separatingAxes = t1c.normals + t2c.normals
        mtv = [0,0]
        # determine the scores(which is length of the vector projected onto the separating axes)
        # of all points for each separating axis
        smallest_depth = 99999999 # bigg number
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
            overlap1 = t1Max - t2Min  # t1 projected right into t2
            overlap2 = t2Max - t1Min  # t2 projected right into t1
            depth = min(overlap1, overlap2)
            if depth <= 0:
                return [0,0]
            if depth < smallest_depth:
                # choose the smaller magnitude (shallowest)
                if overlap1 > overlap2:
                    direction = 1  # move t1 away along +axis
                else:
                    direction = -1  # move t1 away along -axis
                smallest_depth = depth
                mtv = axis
        return Vector.scalarMult(smallest_depth * direction, mtv)



    def findRectToRect(self, s1px, s1py, s1c, s2px, s2py, s2c):
        left1 = s1px-s1c.width/2
        right1 = s1px+s1c.width / 2
        top1 = s1py - s1c.height / 2
        bottom1 = s1py + s1c.height / 2
        left2 = s2px - s2c.width / 2
        right2 = s2px + s2c.width / 2
        top2 = s2py - s2c.height / 2
        bottom2 = s2py + s2c.height / 2
        overlapX = abs(min(right1,right2) - max(left1,left2))
        overlapY = abs(min(bottom1,bottom2) - max(top1,top2))
        if overlapX < overlapY:
            if s1px > s2px: # is object 1 on right side of object 2
                return [overlapX,0]
            else:
                return [-overlapX,0]
        else:
            if s1py > s2py: # is object 1 below object 2
                return [0,overlapY]
            else:
                return  [0,-overlapY]

    def findRectToPolygon(self, tpx, tpy, tc, spx, spy, sc): #t:triangle, s:square, p:position, c:collider

        #Convert Rect into polygon form and work from there
        rect_points = [
            [-tc.width / 2, -tc.height / 2], # top left
            [-tc.width / 2, tc.height / 2], # bottom left
            [tc.width / 2, tc.height / 2], # bottom right
            [tc.width / 2, -tc.height / 2], # top right
        ]
        return self.findPolygonToPolygon(spx,spy,sc,tpx,tpy,CollisionPolygon(rect_points))
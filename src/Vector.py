#this class is just going to be helper methods needed else where it works on [x,y] list and that's it
import math

def Add(vector1, vector2):
    return [vector1[0]+vector2[0],vector1[1]+vector2[1]]

def Subtract(vector1, vector2):
    return [vector1[0]-vector2[0], vector1[1]-vector2[1]]

def scalarMult(scalar, vector):
    return [scalar*vector[0], scalar*vector[1]]

def scalerDiv(vector, scalar):
    return [vector[0]/scalar, vector[1]/scalar]

def Dot(vector1, vector2):
    return (vector1[0]*vector2[0]) + (vector1[1]*vector2[1])

def Cross(vector1, vector2):
    return


def Sum(VectorList):
    if len(VectorList)==0:
        return [0,0]
    vector = [0,0]
    for i in VectorList:
        vector = Add(vector, i)
    return vector

def Unit(vector):
    magnitude = Magnitude(vector)
    if magnitude==0:
        return [0,0]
    return [vector[0]/magnitude, vector[1]/magnitude]

def Magnitude(vector):
    return math.sqrt(vector[0]**2+vector[1]**2)

def Normal(vector):
    return [-vector[1], vector[0]]

#these are points btw checks if the points are following a counter clockwise orientation
def ccw(P, Q, R):
    return (R[1] - P[1]) * (Q[0] - P[0]) > (Q[1] - P[1]) * (R[0] - P[0])


def forceCounterClockwise(points): # returns a polygon shape with a ccw winding
    # ensure CounterClockwise property apparently that's good for polygons
    for i in range(len(points)):
        P1 = i % len(points)
        P2 = (i + 1) % len(points)
        P3 = (i + 2) % len(points)
        if not ccw(points[P1], points[P2], points[P3]):
            # swap the points to enforce CCW
            points[P2], points[P3] = points[P3], points[P2]
    return points

import math

class Vector:

    def __init__ (self, x, y, z):

        self.x = x
        self.y = y
        self.z = z


    def __repr__(self):
        return f"x={self.x}, y={self.y}, z={self.z}"


def toVector (point_a, point_b):

    x1 = point_a.x - point_b.x
    y1 = point_a.y - point_b.y
    z1 = point_a.z - point_b.z

    return Vector(x1, y1, z1)

def magnitude (vector_a):

    x = pow(vector_a.x, 2)
    y = pow(vector_a.y, 2)
    z = pow(vector_a.z, 2)

    mag = math.sqrt(x + y + z)

    return mag

def dotProduct (vector_a, vector_b):

    newx = vector_a.x * vector_b.x
    newy = vector_a.y * vector_b.y
    newz = vector_a.z * vector_b.z
    dot = newx + newy + newz

    return dot


def jointAngle2D(vector_a, vector_b):

    dot = (vector_a.x * vector_b.x) + (vector_a.y * vector_b.y)

    magA = math.sqrt(vector_a.x**2 + vector_a.y**2)
    magB = math.sqrt(vector_b.x**2 + vector_b.y**2)

    val = dot / (magA * magB)

    val = max(-1, min(1, val))

    thetaRad = math.acos(val)

    thetaDeg = math.degrees(thetaRad)

    return thetaDeg
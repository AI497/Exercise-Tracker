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

def jointAngle(point_a, point_b, point_c):
    """Angle in degrees at point_b, between segments b->a and b->c (3D)."""

    vector_a = toVector(point_a, point_b)
    vector_c = toVector(point_c, point_b)

    mags = magnitude(vector_a) * magnitude(vector_c)
    if mags == 0:
        return 0.0

    val = max(-1, min(1, dotProduct(vector_a, vector_c) / mags))

    return math.degrees(math.acos(val))


if __name__ == "__main__":
    b = Vector(0, 0, 0)
    assert round(jointAngle(Vector(1, 0, 0), b, Vector(0, 1, 0))) == 90
    assert round(jointAngle(Vector(1, 0, 0), b, Vector(-1, 0, 0))) == 180
    assert round(jointAngle(Vector(1, 0, 0), b, Vector(1, 0, 0))) == 0
    assert round(jointAngle(Vector(1, 0, 0), b, Vector(1, 0, 1))) == 45
    assert jointAngle(b, b, Vector(1, 0, 0)) == 0.0
    print("ok")

"""
Vector math for measuring joint angles.

Any object with .x, .y, .z attributes works as a point, including MediaPipe landmarks.
Run this file directly to self-check the math:  python joint_calculations.py
"""

import math


class Vector:

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"x={self.x}, y={self.y}, z={self.z}"


def toVector(point_a, point_b):
    """Vector pointing from point_b to point_a."""
    return Vector(point_a.x - point_b.x,
                  point_a.y - point_b.y,
                  point_a.z - point_b.z)


def magnitude(vector):
    """Length of a vector."""
    return math.sqrt(vector.x**2 + vector.y**2 + vector.z**2)


def dotProduct(vector_a, vector_b):
    return vector_a.x * vector_b.x + vector_a.y * vector_b.y + vector_a.z * vector_b.z


def jointAngle(point_a, point_b, point_c):
    """
    Angle in degrees at point_b, between the segments b->a and b->c.
    e.g. jointAngle(shoulder, elbow, wrist) is the elbow angle (180 = arm straight).
    """
    vector_a = toVector(point_a, point_b)
    vector_c = toVector(point_c, point_b)

    lengths = magnitude(vector_a) * magnitude(vector_c)
    if lengths == 0:  # two points on top of each other: no angle
        return 0.0

    # cos(angle) = dot / lengths; clamp to [-1, 1] so rounding errors can't break acos
    cos_angle = max(-1, min(1, dotProduct(vector_a, vector_c) / lengths))

    return math.degrees(math.acos(cos_angle))


if __name__ == "__main__":
    b = Vector(0, 0, 0)
    assert round(jointAngle(Vector(1, 0, 0), b, Vector(0, 1, 0))) == 90
    assert round(jointAngle(Vector(1, 0, 0), b, Vector(-1, 0, 0))) == 180
    assert round(jointAngle(Vector(1, 0, 0), b, Vector(1, 0, 0))) == 0
    assert round(jointAngle(Vector(1, 0, 0), b, Vector(1, 0, 1))) == 45
    assert jointAngle(b, b, Vector(1, 0, 0)) == 0.0
    print("ok")

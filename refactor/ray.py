from vector import Vector3

class Hit:
    def __init__(self, t, point, normal):
        self.t = t
        self.point = point
        self.normal = normal

class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    def at(self, t):
        return self.origin + (self.direction * t)

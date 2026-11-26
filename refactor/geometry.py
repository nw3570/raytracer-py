import numpy as np
import math
from vector import Vector3
from ray import Hit, Ray

EPSILON = 1e-8

def tonumpy(p: Vector3, w = 1):
    return np.array([p.x, p.y, p.z, w])

def tovec3(p: np.ndarray):
    if p[3] != 0:
        return Vector3(p[0]/p[3], p[1]/p[3], p[2]/p[3])
    else:
        return Vector3(p[0], p[1], p[2])

def scale(x, y, z):
    return np.diag([x, y, z, 1])

def rotz(theta):
    c = math.cos(theta)
    s = math.sin(theta)
    return np.array([
        [c, -s, 0, 0],
        [s, c, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

def rotx(theta):
    c = math.cos(theta)
    s = math.sin(theta)
    return np.array([
        [1, 0, 0, 0],
        [0, c, -s, 0],
        [0, s, c, 0],
        [0, 0, 0, 1]
    ])

def roty(theta):
    c = math.cos(theta)
    s = math.sin(theta)
    return np.array([
        [c, 0, s, 0],
        [0, 1, 0, 0],
        [-s, 0, c, 0],
        [0, 0, 0, 1]
    ])

def translate(dx, dy, dz):
    return np.array([
        [1, 0, 0, dx],
        [0, 1, 0, dy],
        [0, 0, 1, dz],
        [0, 0, 0, 1]
    ])

class Triangle:
    def __init__(self, name, v0, v1, v2, mesh):
        self.name = name
        self.a = v0
        self.b = v1
        self.c = v2
        self.mesh = mesh
        self.centroid = (a + b + c) / 3

class TriangularMesh:
    def __init__(self, name, v, vn, fv, fvn):
        self.name = name
        self.vertices = v
        self.normals = vn
        self.vertices_idx = fv
        self.normals_idx = fvn

    @staticmethod
    def _moller_trumbore(ray, a, b, c):
        edge1 = b - a
        edge2 = c - a

        p = ray.direction.cross(edge2)
        det = p.dot(edge1)

        if abs(det) < EPSILON:
            return None

        inv_det = 1.0 / det
        s = ray.origin - a
        u = inv_det * p.dot(s)

        if u < -EPSILON or u > 1.0 + EPSILON:
            return None

        q = s.cross(edge1)
        v = inv_det * q.dot(ray.direction)

        if v < -EPSILON or v + u >  1.0 + EPSILON:
            return None

        t = inv_det * edge2.dot(q)
        return u, v, t


    def hit(self, ray):
        nfaces = len(self.vertices_idx) // 3
        hits = []

        for i in range(0, nfaces):
            idx_start = 3 * i
            idx_end = idx_start + 3

            v0, v1, v2 = self.vertices_idx[idx_start : idx_end]
            res = TriangularMesh._moller_trumbore(
                ray,
                self.vertices[v0], self.vertices[v1], self.vertices[v2]
            )

            if res is None:
                continue

            u, v, t = res
            w = 1.0 - u - v

            n0, n1, n2 = self.normals_idx[idx_start : idx_end]
            normal = (
                u * self.normals[n1]
                + v * self.normals[n2]
                + w * self.normals[n0]
            ).normalized()

            hits.append(Hit(t, ray.at(t), normal))

        return hits

class Sphere:
    def __init__(self, name, pos, r):
        self.r = r
        self.name = name
        #self.material = mat
 
        self.model = np.eye(4)
        self.model[0, 3] = pos.x
        self.model[1, 3] = pos.y
        self.model[2, 3] = pos.z

    def pos(self):
        return Vector3(self.model[0, 3], self.model[1, 3], self.model[2, 3])

    def hit(self, ray):
        invmodel = np.linalg.inv(self.model)

        O = ray.origin
        O = invmodel @ tonumpy(O)
        O = tovec3(O)
        
        D = invmodel @ tonumpy(ray.direction, 0)
        D = tovec3(D)
        
        C = Vector3(0, 0, 0)
        a = D.dot(D)
        b = (D*2).dot(O - C)
        c = (O-C).dot(O - C) - self.r**2
        delta = (b**2) - 4 * a * c
    
        normal_matrix = invmodel.T
        def to_world(t):
            p_local = O + t * D
            n_local = (p_local - C).normalized()
            p_world = tovec3(self.model @ tonumpy(p_local))
            n_world = tovec3(normal_matrix @ tonumpy(n_local, 0)).normalized()
            return Hit(t, p_world, n_world)
        eps = 1.0e-9
        if delta < -eps:
            return []
        elif abs(delta) < eps:
            t = -b/(2*a)
            p = O + t * D
            n = (p - C).normalized()
            return [to_world(t)]
        else:
            t1 = (-b + math.sqrt(delta))/(2*a)
            t2 = (-b - math.sqrt(delta))/(2*a)
            p1 = O + t1 * D
            n1 = (p1 - C).normalized()
            p2 = O + t2 * D
            n2 = (p2 - C).normalized()
    
            return [to_world(t1), to_world(t2)]

class Plan:
    def __init__(self, name, point, normal):
        self.normal = normal
        self.point = point
        #self.material = mat
        self.name = name

    def hit(self, ray):
        d = ray.direction.dot(self.normal)
        if abs(d) > 0.0001: 
            t = (self.point - ray.origin).dot(self.normal)/d
            p = ray.origin + t * ray.direction
            #print(" ray  = " , ray.origin)
            return [Hit(t, p, self.normal)]
        else:
            return []

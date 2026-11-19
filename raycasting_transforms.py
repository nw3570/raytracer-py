import math
from vector import Vector3
import numpy as np

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

class Light:
    def __init__(self, pos, color):
        self.position = pos
        self.color = color

class Material:
    def __init__(self, albedo, ka, kd, ks):
        self.albedo = albedo
        self.ka = ka
        self.kd = kd
        self.ks = ks

class Image:
    def __init__(self, W, H, background=None):
        if background is None:
            background = [255, 255, 255, 255]
        self.W = W
        self.H = H
        self.background = background
        self.data = [0] * (self.W * self.H * 4)
        for i in range(H):
            for j in range(W):
                self.data[i * (4*W) + j * 4] = background[0]
                self.data[i * (4*W) + j * 4+1] = background[1]
                self.data[i * (4*W) + j * 4+2] = background[2]
                self.data[i * (4*W) + j * 4+3] = background[3]
    
    def set_pixel(self, i, j, cor):
        self.data[i * (4*self.W) + j * 4] = cor[0]
        self.data[i * (4*self.W) + j * 4+1] = cor[1]
        self.data[i * (4*self.W) + j * 4+2] = cor[2]
        self.data[i * (4*self.W) + j * 4+3] = cor[3]
    
    def get_pixel(self, i , j):
        cor = [0, 0, 0, 0]
        cor[0] = self.data[i * (4*self.W) + j * 4]
        cor[1] = self.data[i * (4*self.W) + j * 4+1]
        cor[2] = self.data[i * (4*self.W) + j * 4+2]
        cor[3] = self.data[i * (4*self.W) + j * 4+3]
        return cor

class Camera:
    def __init__(self, pos, fov):
        self.pos = pos
        self.fov = fov

class Hit:
    def __init__(self, t, point, normal):
        self.t = t
        self.point = point
        self.normal = normal

class Sphere:
    def __init__(self, name, pos, r, mat):
        self.r = r
        self.name = name
        self.material = mat
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
    def __init__(self, name, point, normal, mat):
        self.normal = normal
        self.point = point
        self.material = mat
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

class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction


def raycasting(img, camera, scene, background=None):
    if background is None:
        background = [255, 255, 255, 255]
    h = math.tan( (camera.fov/2) * math.pi/180.0 )
    w = (img.W/img.H) * h
    for i in range(img.H):
        for j in range(img.W):
            xndc = 2 * (j + 0.5)/img.W - 1
            yndc = 1 - 2 * (i + 0.5)/img.H
            p = camera.pos + Vector3(xndc * w, yndc * h, -1)
            raydir = (p - camera.pos).normalized()
            #print("x, y = ", xndc, " : ", yndc) 
            ray = Ray(camera.pos,  raydir)
            t = float("inf")
            objint = None
            shit = None #selected hit
            for obj in scene:
                hits = obj.hit(ray)
                for hit in hits:
                    if hit.t > 1 and hit.t < t:
                        t = hit.t
                        objint = obj
                        shit = hit
            if objint is not None:
                corf  = objint.material.albedo
                N = shit.normal
                P = shit.point
                L = (light.position-P).normalized()
                m = objint.material
                D = max(0, L.dot(N))
                R = (m.ka * envlight[0] * m.albedo[0]  + m.kd * light.color[0] * m.albedo[0] * D) * 255
                G = (m.ka * envlight[1] * m.albedo[1]  + m.kd * light.color[1] * m.albedo[1] * D) * 255
                B = (m.ka * envlight[2] * m.albedo[2]  + m.kd * light.color[2] * m.albedo[2] * D) * 255

                R = min(R, 255)
                G = min(G, 255)
                B = min(B , 255)

                corf = [int(R), int(G), int(B), 255]

                img.set_pixel(i, j, corf)
            else:
                img.set_pixel(i, j, background)
    return img

def save_img(path, img):
    with open(path, "w+") as f:
        f.write("P3\n")
        f.write(f"{img.W} {img.H}\n")
        f.write("255\n")
        for i in range(img.H):
            for j in range(img.W):
                pixel = img.get_pixel(i, j)
                f.write(f"{pixel[0]} {pixel[1]} {pixel[2]}")
                if j < img.W - 1:
                    f.write(" ")
            f.write("\n")


light = Light(Vector3(0, 10, -50), [0.9, 0.9, 0.9, 1])
envlight = [1, 1, 1, 1]
scene = [Sphere("esfera", Vector3(0, 0, 0), 1, Material([1, 0, 0, 1], 0.4, 1, 1) )]
plan = Plan("plano", Vector3(0, -1, 0), Vector3(0.0, -1.0, 0.0), Material([0, 1, 1, 1], 0.1, 1, 1))

scene.append(plan)

img = Image(400, 400)
camera = Camera(Vector3(0, 0, 10), 90)

TS  = []
TS.append(scale(2, 2, 2))
TS.append(translate(0,10, -10) @ scale(10, 3, 3))
TS.append(translate(0, 10, -10) @ rotz(45 * math.pi/180.0) @ scale(10, 3, 3))
TS.append(translate(1, 3, -10) @ scale(4, 1, 1))
TS.append(scale(4, 1, 1) @ translate(1, 3, -10))

i = 0
for t in TS:
    img = raycasting(img, camera, scene)
    save_img(f"output_{i}.ppm", img)
    i += 1
    scene[0].model = t

img = raycasting(img, camera, scene)
save_img(f"output_{i}.ppm", img)

#scene[0].model = scene[0].model @ scale(2, 2, 2)
#img = raycasting(img, camera, scene)
#save_img("output_02.ppm", img)




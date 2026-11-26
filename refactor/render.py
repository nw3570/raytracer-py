from shading import Material, Light, phong
from vector import Vector3
from ray import Ray, Hit
import math

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

class SceneObject:
    def __init__(self, geometry, material):
        self.geometry = geometry
        self.material = material

   #def hit(self, ray):
   #    return self.geometry.hit(ray)

class Scene:
    def __init__(self, background=None, env_light_color=None):
        if background is None:
            self.background = [255, 255, 255, 255]
        else:
            self.background = background
        
        if env_light_color is None:
            self.env_light_color = Vector3(1.0, 1.0, 1.0)
        else:
            self.env_light_color = env_light_color

        self.objects = []
        self.lights = []


def raycasting(img, camera, scene):
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
            hit_obj = None
            hit_min = None

            for obj in scene.objects:
                hits = obj.geometry.hit(ray)
                for hit in hits:
                    if hit.t > 1 and hit.t < t:
                        t = hit.t
                        hit_obj = obj
                        hit_min = hit
            
            if hit_obj is not None:
                color_vec = phong(
                    scene.lights, scene.env_light_color,
                    hit_min.point, hit_min.normal, camera.pos,
                    hit_obj.material
                )

                color_vec.clamp(0, 1.0)

                corf = [
                    int(color_vec.x * 255), # R
                    int(color_vec.y * 255), # G
                    int(color_vec.z * 255), # B
                    255
                ]

                img.set_pixel(i, j, corf)
            else:
                img.set_pixel(i, j, scene.background)
    return img

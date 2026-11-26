from vector import Vector3
from wavefront import loader
from render import Scene, SceneObject, Camera, Image, raycasting
from geometry import Sphere, Plan, TriangularMesh
from shading import Material, Light
import sys

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

img = Image(400, 400)
camera = Camera(Vector3(0, 0, 2), 90.0)
cena = Scene()

metal = Material(
    albedo=Vector3(0.8, 0.8, 0.9),
    ka=0.2, kd=0.4, ks=0.9, ns=64
)
snow = Material(
    albedo=Vector3(0.95, 0.97, 1.0),
    ka=0.85, kd=0.85, ks=0.15, ns=12
)

esfera = SceneObject(
    Sphere("esfera", Vector3(0, 0, -5.0), 1.0),
    metal
)
plano = SceneObject(
    Plan("plano", Vector3(0, -1.0, 0), Vector3(0, 1.0, 0)),
    snow
)

if len(sys.argv) > 1:
    v, vn, fv, fvn = loader(sys.argv[1])

    malha = SceneObject(TriangularMesh("malha", v, vn, fv, fvn), metal)
    cena.objects.append(malha)

cena.objects.append(esfera)
cena.objects.append(plano)

lampada = Light(position=Vector3(0, 1.0, 5.0), color=Vector3(1.0, 1.0, 1.0))

cena.lights.append(lampada)

raycasting(img, camera, cena)
save_img("output.ppm", img)

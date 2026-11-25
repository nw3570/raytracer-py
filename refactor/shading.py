from vector import Vector3

class Material:
    def __init__(self, albedo, ka, kd, ks, ns):
        self.albedo = albedo
        self.ka = ka
        self.kd = kd
        self.ks = ks
        self.ns = ns

class Light:
    def __init__(self, position, color):
        self.position = position
        self.color = color

    def direction(self, point):
        return (self.position - point).normalized()

    def phong_diffuse(self, light_dir, normal, base_color, kd):
        nl = normal.dot(light_dir)

        if nl <= 0.0:
            return Vector3.zero()

        return (self.color * kd).hadamard(base_color * nl)

    def phong_specular(self, light_dir, normal, view_dir, ks, ns):
        nl = normal.dot(light_dir)
        reflection = light_dir.reflect(normal)
        rv = reflection.dot(view_dir)

        if rv <= 0.0:
            return Vector3.zero()

        return self.color * ks * rv ** ns


    def blinn_phong_specular(self, light_dir, normal, view_dir, ks, ns):
        halfway = (light_dir + view_dir).normalized()
        hn = halfway.dot(normal)

        if hn <= 0.0:
            return Vector3.zero()

        return self.color * ks * hn ** ns

def phong_ambient(light_color, base_color, ka):
    return base_color.hadamard(light_color * ka)

def phong(lights, ambient_light_color, point, normal, eye, material):
    view_dir = (eye - point).normalized()

    ambient = phong_ambient(ambient_light_color, material.albedo, material.ka)
    diffuse = Vector3.zero()
    specular = Vector3.zero()

    for light in lights:
        light_dir = light.direction(point)

        diffuse += light.phong_diffuse(
            light_dir, normal,
            material.albedo, material.kd
        )

        specular += light.blinn_phong_specular(
            light_dir, normal, view_dir,
            material.ks, material.ns
        )
    
    return ambient + diffuse + specular

def normal_shade(normal):
    return 0.5 * (normal + Vector3(1.0, 1.0, 1.0))

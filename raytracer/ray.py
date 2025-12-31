import numpy as np
import math
from surfaces.cube import Cube
from surfaces.infinite_plane import InfinitePlane
from surfaces.sphere import Sphere

class Ray:
    def __init__(self, camera_point, pixel_point):
        self.camera_point = np.array(camera_point, dtype=float)
        self.pixel_point = np.array(pixel_point, dtype=float)

        self.V = self.pixel_point - self.camera_point
        self.V = self.V / np.linalg.norm(self.V)
    
    def find_ray_closest_intersection(self, surfaces):
        t_min = math.inf
        closest_obj = None

        for obj in surfaces:
            t = obj.find_intersection(self)
            if t is not None and t < t_min:
                t_min = t
                closest_obj = obj
        if closest_obj is None:
            return None, None, None
        
        closest_hit_point = self.camera_point + t_min * self.V
        return t_min, closest_hit_point, closest_obj
    
    def visible_factor(self, objects, max_distance, materials):
        light_factor = 1.0
        for obj in objects:
            t = obj.find_intersection(self)
            if t is None:
                continue
            if 1e-4 < t < max_distance:
                mat = materials[obj.material_index - 1]
                light_factor *= mat.transparency 
                if light_factor == 0:
                    return 0.0
        return light_factor

        
    def find_ray_closest_object(self, objects):
        t_min, closest_hit_point, closest_obj = self.find_ray_closest_intersection(objects)
        return closest_obj

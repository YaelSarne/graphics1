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
    
    def find_ray_closest_intersection(self, objects):
        t_min = math.inf
        closest_hit_point = np.array([math.inf,math.inf,math.inf], dtype=float)
        closest_obj = None
        surface_types = (Sphere, Cube, InfinitePlane)

        for obj in objects:
            if not isinstance(obj, surface_types):
                continue
            hit_point, t = obj.find_intersection(self)
            if hit_point is None or t is None:
                continue
            if t < t_min:
                t_min = t
                closest_hit_point = hit_point
                closest_obj = obj
        if closest_obj is None:
            return None, None, None
        return t_min, closest_hit_point, closest_obj
    
    def is_visible(self, objects):
        surface_types = (Sphere, Cube, InfinitePlane)
        for obj in objects:
            if not isinstance(obj, surface_types):
                continue
            hit_point, t = obj.find_intersection(self)
            if hit_point is None or t is None:
                continue
            else:
                return False
        return True

        
    def find_ray_closest_object(self, objects):
        t_min, closest_hit_point, closest_obj = self.find_ray_closest_intersection(objects)
        return closest_obj

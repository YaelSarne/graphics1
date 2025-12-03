import numpy as np
import math

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
        for obj in objects:
            result = obj.find_intersection(self)
            if result is None:
                continue
            hit_point, t = result
            if t < t_min:
                t_min = t
                closest_hit_point = hit_point
                closest_obj = obj
        if closest_obj is None:
            return None, None, None
        return t_min, closest_hit_point, closest_obj
        

import numpy as np
import math

class Sphere:
    def __init__(self, position, radius, material_index):
        self.position = position
        self.radius = radius
        self.material_index = material_index

    def find_intersection(self, ray):
        """Find sphere intersection with ray using geometric method"""
        
        position_np_point = np.array(self.position, dtype=float)
            
        L = position_np_point - ray.camera_point
 
        t_ca = np.dot(L, ray.V)
        if (t_ca < 0):
            return 0
        
        d2 = np.dot(L, L)- t_ca**2 
        if (d2 > self.radius**2):
            return 0
        
        t_hc = math.sqrt(self.radius**2-d2)
        t1 = t_ca - t_hc
        t2 = t_ca + t_hc

        if t1 >= 0 and t2 >= 0:
            t = min(t1, t2)
        elif t1 >= 0:
            t = t1           
        elif t2 >= 0:
            t = t2
        
        hit_point = ray.camera_point + t * ray.V
        return hit_point, t

import numpy as np
import math

class Sphere:
    def __init__(self, position, radius, material_index):
        self.position =  np.array(position, dtype=float)
        self.radius = radius
        self.material_index = material_index

    def find_intersection(self, ray):
        """Find sphere intersection with ray using geometric method"""
        epsilon = 1e-4
        L = self.position - ray.camera_point
        t_ca = np.dot(L, ray.V)
        if (t_ca < 0):
            return None
        
        d2 = np.dot(L, L)- t_ca**2 
        if (d2 > self.radius**2):
            return None
        
        t_hc = math.sqrt(self.radius**2-d2)
        t1 = t_ca - t_hc
        t2 = t_ca + t_hc

        if t1 > epsilon:
            return t1
        elif t2 > epsilon:
            return t2      
        else:
            return None

    def get_normal_from_hit_point(self, hit_point):
        if hit_point is None:
            return None
        normal = hit_point - self.position
        normal = normal / np.linalg.norm(normal)
        return normal
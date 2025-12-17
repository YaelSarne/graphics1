import numpy as np
import math

class Sphere:
    def __init__(self, position, radius, material_index):
        self.position =  np.array(position, dtype=float)
        self.radius = radius
        self.material_index = material_index

    def find_intersection(self, ray):
        """Find sphere intersection with ray using geometric method"""
                    
        L = self.position - ray.camera_point
 
        t_ca = np.dot(L, ray.V)
        if (t_ca < 0):
            return None, None
        
        d2 = np.dot(L, L)- t_ca**2 
        if (d2 > self.radius**2):
            return None, None
        
        t_hc = math.sqrt(self.radius**2-d2)
        t1 = t_ca - t_hc
        t2 = t_ca + t_hc

        if t1 >= 0 and t2 >= 0:
            t = min(t1, t2)
        elif t1 >= 0:
            t = t1           
        elif t2 >= 0:
            t = t2
        else:
            return None, None
        
        hit_point = ray.camera_point + t * ray.V

        return hit_point, t

    def get_normal_from_hit_point(self, hit_point):
        if hit_point is None:
            return None
        normal = hit_point - self.position
        normal = normal / np.linalg.norm(normal)
        return normal

    def get_hit_point(self, ray):
        hit_point, t = self.find_intersection(ray)
        return hit_point
    
    def get_normal_from_ray(self, ray):
        hit_point = self.get_hit_point(ray)
        if hit_point is None:
            return None, None
        normal = self.get_normal_from_hit_point(hit_point)
        return normal, hit_point
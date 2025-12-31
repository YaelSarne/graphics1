import math
import numpy as np

class Cube:
    def __init__(self, position, scale, material_index):
        self.position = np.array(position, dtype=float)
        self.scale = scale
        self.material_index = material_index

    def find_intersection(self, ray):
        """Find cube intersection with ray"""
        epsilon = 1e-5
        half = self.scale/2.0

        min_bounds = self.position - half
        max_bounds = self.position + half

        t_near = -math.inf
        t_far = math.inf

        # intersections with P = P0 + tV, for each coordinate (x=0,y=1,z=2)
        for i in range(3):
            if abs(ray.V[i]) < 1e-6: # ray parrallel 
                if ray.camera_point[i] < min_bounds[i] or ray.camera_point[i] > max_bounds[i]:
                    return None
                # always in bound
                t1 = -math.inf 
                t2 = math.inf
            else:
                t1 = (min_bounds[i] - ray.camera_point[i]) / ray.V[i]
                t2 = (max_bounds[i] - ray.camera_point[i]) / ray.V[i]
                if t1 > t2:  #V[i] < 0 , ray goes negative
                    t1, t2 = t2, t1

                t_near = max(t_near, t1)
                t_far = min(t_far, t2)
        
        if t_near > t_far:
            return None
        if t_far < epsilon: #t_min = 0, cube is behind camera
            return None
        if t_near > epsilon:
            return t_near
        else:
            return t_far

    def get_normal_from_hit_point(self, hit_point):
        if hit_point is None:
            return None

        d = hit_point - self.position

        # find the farests asix 
        max_val = abs(d[0])
        axis = 0

        for i in range(1, 3):
            if abs(d[i]) > max_val:
                max_val = abs(d[i])
                axis = i

        normal = np.zeros(3)
        normal[axis] = 1.0 if d[axis] > 0 else -1.0

        return normal
    

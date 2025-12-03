import math

class Cube:
    def __init__(self, position, scale, material_index):
        self.position = position
        self.scale = scale
        self.material_index = material_index

    def find_intersection(self, ray):
        """Find cube intersection with ray"""
        half = self.scale/2
        min_bounds = [self.position[0] - half , self.position[1] - half, self.position[2] - half]
        max_bounds = [self.position[0] + half, self.position[1] + half, self.position[2] + half]
        
        t_near = -math.inf
        t_far = math.inf

        # intersections with P = P0 + tV, for each coordinate (x=0,y=1,z=2)
        for i in range(3):
            if ray.V[i] == 0: # ray parrallel 
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
        if t_far < 0: #t_min = 0, cube is behind camera
            return None
        if t_near < 0:
            t = t_far
        else:
            t = t_near
        hit_point = ray.camera_point + t*ray.V
        return hit_point, t

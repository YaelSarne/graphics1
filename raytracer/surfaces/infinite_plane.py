import numpy as np

class InfinitePlane:
    def __init__(self, normal, offset, material_index):
        self.normal = np.array(normal, dtype=float)
        self.normal = self.normal / np.linalg.norm(self.normal)

        self.offset = offset
        self.material_index = material_index

    def find_intersection(self, ray):
        epsilon = 1e-4
        V_N_dot_product = np.dot(ray.V, self.normal)
        if abs(V_N_dot_product) < epsilon:
            return None # Ray is parrallel to plane
        
        t = (self.offset - np.dot(ray.camera_point, self.normal)) / V_N_dot_product
        if t < epsilon: # plane is behind camera
            return None
        return t
    
    def get_normal_from_hit_point(self, hit_point):
        return self.normal
        
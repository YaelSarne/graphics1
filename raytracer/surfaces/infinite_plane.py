import numpy as np

class InfinitePlane:
    def __init__(self, normal, offset, material_index):
        self.normal = np.array(normal, dtype=float)
        self.offset = offset
        self.material_index = material_index

    def find_intersection(self, ray):
        V_N_dot_product = np.dot(ray.V, self.normal)
        if V_N_dot_product == 0: # Ray is parrallel to plane
            if np.dot(ray.camera_point, self.normal) == self.offset: #camera point is on plane
                return ray.camera_point, 0.0
            return None, None
        t = (self.offset - np.dot(ray.camera_point, self.normal)) / V_N_dot_product
        if t < 0: # plane is behind camera
            return None, None
        hit_point = ray.camera_point + t * ray.V
        return hit_point, t
    
    def get_hit_point(self, ray):
        hit_point, t = self.find_intersection(ray)
        return hit_point

    def get_normal_from_hit_point(self, hit_point):
        if hit_point is None:
            return None
        N = self.normal / np.linalg.norm(self.normal)
        return N

    def get_normal_from_ray(self, ray):
        hit_point = self.get_hit_point(ray)
        if hit_point is None:
            return None, None
        N = self.get_normal_from_hit_point(hit_point)
        return N, hit_point

        
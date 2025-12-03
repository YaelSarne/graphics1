import numpy as np

class InfinitePlane:
    def __init__(self, normal, offset, material_index):
        self.normal = normal
        self.offset = offset
        self.material_index = material_index

    def find_intersection(self, ray):
        N = np.array(self.normal, dtype=float)
        V_N_dot_product = np.dot(ray.V,N)
        if V_N_dot_product == 0: # Ray is parrallel to plane
            if np.dot(ray.camera_point, N) == self.offset: #camera point is on plane
                return ray.camera_point, 0.0
            return None, None
        t = (self.offset - np.dot(ray.camera_point, N)) / V_N_dot_product
        if t < 0: # plane is behind camera
            return None, None
        hit_point = ray.camera_point + t * ray.V
        return hit_point, t

        
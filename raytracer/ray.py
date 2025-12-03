import numpy as np

class Ray:
    def __init__(self, camera_point, pixel_point):
        self.camera_point = np.array(camera_point, dtype=float)
        self.pixel_point = np.array(pixel_point, dtype=float)

        self.V = self.pixel_point - self.camera_point
        self.V = self.V / np.linalg.norm(self.V)
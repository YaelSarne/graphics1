import numpy as np
from ray import Ray

class Camera:
    def __init__(self, position, look_at, up_vector, screen_distance, screen_width, width_pixels, height_pixels):
        self.position = np.array(position, dtype=float)
        self.look_at = np.array(look_at, dtype=float)
        self.up_vector = np.array(up_vector, dtype=float)
        self.screen_distance = screen_distance
        self.screen_width = screen_width

        #represent screen and parameters that will help building pixel grid
        looking_ray = Ray(position, look_at)
        screen_middle = position + looking_ray.V * screen_distance
        up_v = -(1/looking_ray.V)  #need to check if that works and normalize it!!!
        screen_width_v = np.cross(up_v, looking_ray.V) #normalize that two!!!
        pixel_size = screen_width / width_pixels
        screen_height = pixel_size * height_pixels
        screen_top_right = screen_middle + up_v *screen_height / 2 + screen_width_v * screen_width /2
        top_right_pixel = screen_top_right - up_v * pixel_size / 2 - screen_width_v * pixel_size / 2
        self.top_right_pixel = top_right_pixel
        self.pixel_size = pixel_size
        self.height_v = up_v
        self.width_v = screen_width_v



    """

    if i choose to mobe the code back to ray tracer:
        looking_ray = Ray(camera.position, camera.look_at)
        screen_middle = position + looking_ray.V * camera.screen_distance
        up_v = -(1/looking_ray.V)  #need to check if that works and normalize it!!!
        screen_width_v = np.cross(up_v, looking_ray.V)
        pixel_size = camera.screen_width / args.width
        screen_height = pixel_size * args.height
        screen_top_right = screen_middle + up_v *screen_height / 2 + screen_width_v * camera.screen_width /2
        top_right_pixel = top_right -
    """
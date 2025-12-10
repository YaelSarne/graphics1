import argparse
from PIL import Image
import numpy as np

from camera import Camera
from light import Light
from material import Material
from scene_settings import SceneSettings
from surfaces.cube import Cube
from surfaces.infinite_plane import InfinitePlane
from surfaces.sphere import Sphere
from ray import Ray


def parse_scene_file(file_path, width_pixels, height_pixels):
    objects = []
    camera = None
    scene_settings = None
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            obj_type = parts[0]
            params = [float(p) for p in parts[1:]]
            if obj_type == "cam":
                camera = Camera(params[:3], params[3:6], params[6:9], params[9], params[10], width_pixels, height_pixels)
            elif obj_type == "set":
                scene_settings = SceneSettings(params[:3], params[3], params[4])
            elif obj_type == "mtl":
                material = Material(params[:3], params[3:6], params[6:9], params[9], params[10])
                objects.append(material)
            elif obj_type == "sph":
                sphere = Sphere(params[:3], params[3], int(params[4]))
                objects.append(sphere)
            elif obj_type == "pln":
                plane = InfinitePlane(params[:3], params[3], int(params[4]))
                objects.append(plane)
            elif obj_type == "box":
                cube = Cube(params[:3], params[3], int(params[4]))
                objects.append(cube)
            elif obj_type == "lgt":
                light = Light(params[:3], params[3:6], params[6], params[7], params[8])
                objects.append(light)
            else:
                raise ValueError("Unknown object type: {}".format(obj_type))
    return camera, scene_settings, objects


def save_image(image_array, output_filename): # <-- הוספת ארגומנט
    image = Image.fromarray(np.uint8(image_array))

    # שימוש בשם הקובץ שסופק
    image.save(output_filename) # <-- שימוש בארגומנט



def main():
    parser = argparse.ArgumentParser(description='Python Ray Tracer')
    parser.add_argument('scene_file', type=str, help='Path to the scene file')
    parser.add_argument('output_image', type=str, help='Name of the output image file')
    parser.add_argument('--width', type=int, default=500, help='Image width')
    parser.add_argument('--height', type=int, default=500, help='Image height')
    args = parser.parse_args()
    # Parse the scene file
    
    
    camera, scene_settings, objects = parse_scene_file(args.scene_file, args.width, args.height)

    image_array = np.zeros((args.height, args.width, 3), dtype=np.uint8)
    #create pixel grid
    row_head = camera.top_right_pixel
    for y in range(args.height):
        curr_pixel = row_head
        for x in range(args.width):
            curr_ray = Ray(camera.position, curr_pixel)
            t_min, closest_hit_point, closest_obj = curr_ray.find_ray_closest_intersection(objects)
            if closest_obj is None:
                color = np.array([0, 0, 0], dtype=np.uint8)            # no hit → black
            elif isinstance(closest_obj, Sphere):
                color = np.array([255, 0, 0], dtype=np.uint8)          # sphere → red
            elif isinstance(closest_obj, Cube):
                color = np.array([0, 255, 0], dtype=np.uint8)          # cube → green
            elif isinstance(closest_obj, InfinitePlane):
                color = np.array([0, 0, 255], dtype=np.uint8)          # plane → blue
            else:
                color = np.array([255, 255, 255], dtype=np.uint8)      # anything else

            image_array[y, x] = color
            curr_pixel = curr_pixel - camera.pixel_size * camera.width_v
        row_head = row_head - camera.pixel_size * camera.height_v


    # TODO: Implement the ray tracer

    # Dummy result
    #image_array = np.zeros((500, 500, 3))

    # Save the output image
    save_image(image_array, args.output_image)


if __name__ == '__main__':
    main()

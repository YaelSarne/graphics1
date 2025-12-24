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
    materials = []
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
                #objects.append(material)
                materials.append(material)
            elif obj_type == "sph":
                sphere = Sphere(params[:3], params[3], int(params[4]))
                objects.append(sphere)
                #print(sphere.material_index)
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
    return camera, scene_settings, objects, materials


def save_image(image_array, output_filename): # <-- הוספת ארגומנט
    final_image = np.clip(image_array * 255, 0, 255).astype(np.uint8)
    image = Image.fromarray(final_image)
    # שימוש בשם הקובץ שסופק
    image.save(output_filename) # <-- שימוש בארגומנט

def get_color(scene_settings, ray, lights, materials, objects, camera, max_iters):
    if max_iters <= 0:
        return np.array(scene_settings.background_color)

    t_min, hit_point, obj = ray.find_ray_closest_intersection(objects)
    if obj is None:
        return np.array(scene_settings.background_color)
        
    material = materials[obj.material_index - 1]
    reflection_color = np.array(material.reflection_color)

    normal, hit_point = obj.get_normal_from_ray(ray)
    normal = normal / np.linalg.norm(normal)
    if np.dot(normal, ray.V) > 0:
        normal = -normal
    
    current_color = np.array(color_by_lights(hit_point, obj, lights, objects, material, camera))
    
    # Reflection
    if np.any(reflection_color > 0):
        reflection_dir = ray.V - 2 * np.dot(ray.V, normal) * normal
        reflection_dir = reflection_dir / np.linalg.norm(reflection_dir)
        
        eps = 1e-4
        reflected_ray = Ray(hit_point + eps * normal, hit_point + eps * normal + reflection_dir)
        reflection_color_val = get_color(scene_settings, reflected_ray, lights, materials, objects, camera, max_iters - 1)
        current_color = (1 - reflection_color) * current_color + reflection_color * reflection_color_val

    # Transparency
    if material.transparency > 0:
        eps = 1e-4
        new_origin = hit_point + eps * ray.V 
        behind_ray = Ray(new_origin, new_origin + ray.V)
        behind_color = get_color(scene_settings, behind_ray, lights, materials, objects, camera, max_iters - 1)
        current_color = material.transparency * behind_color + (1 - material.transparency) * current_color
    return current_color

def get_light_plane_axes(light_dir):
    """Return U, V of the plane"""
    light_dir = light_dir / np.linalg.norm(light_dir)
    
    #choose helper vector
    if abs(light_dir[0]) < 0.1 and abs(light_dir[2]) < 0.1:
        helper = np.array([1.0, 0.0, 0.0]) 
    else:
        helper = np.array([0.0, 1.0, 0.0]) 
        
    #find U vertical to L
    U = np.cross(helper, light_dir)
    U = U / np.linalg.norm(U)

    #find V vertical to L and U
    V = np.cross(light_dir, U)
    V = V / np.linalg.norm(V)

    return U, V

def color_by_lights(closest_hit_point, closest_obj, lights, objects, material, camera):
    eps = 1e-4
    colors = np.array([0.0, 0.0, 0.0])
    for light in lights:

        normal = closest_obj.get_normal_from_hit_point(closest_hit_point)
        observer_ray = Ray(closest_hit_point, camera.position)

        if np.dot(normal, observer_ray.V) < 0:
            normal = -normal
        light_ray = Ray(closest_hit_point + eps * normal, light.position)

        is_visible = light_ray.is_visible(objects)
        light_influence = 1 if is_visible else (1-light.shadow_intensity)
        if light_influence > 0 :
            diff_angle = max(0.0, np.dot(normal, light_ray.V))
            diffuse_light = [light.color[i]*material.diffuse_color[i]*diff_angle for i in range(3)]
            reflected_ray = light_ray.V - 2*np.dot(light_ray.V, normal)*normal
            spec_angle = max(0.0, np.dot(reflected_ray, observer_ray.V))
            specular_light = [light.specular_intensity*light.color[i]*material.specular_color[i]*spec_angle**material.shininess for i in range(3)]
            colors = [colors[i] + light_influence*diffuse_light[i] + light_influence*specular_light[i] for i in range(3)]
    return colors

def create_light_list(objects):
    #probably this is the function to change for soft shadows
    lights = []
    for obj in objects:
        if isinstance(obj, Light):
            lights.append(obj)
    return lights

def compute_color(ray, objects, materials, camera, scene_settings):
    lights = create_light_list(objects)
    return get_color(scene_settings, ray, lights, materials, objects, camera, scene_settings.max_recursions)


def main():
    parser = argparse.ArgumentParser(description='Python Ray Tracer')
    parser.add_argument('scene_file', type=str, help='Path to the scene file')
    parser.add_argument('output_image', type=str, help='Name of the output image file')
    parser.add_argument('--width', type=int, default=500, help='Image width')
    parser.add_argument('--height', type=int, default=500, help='Image height')
    args = parser.parse_args()
    # Parse the scene file
    
    
    camera, scene_settings, objects, materials = parse_scene_file(args.scene_file, args.width, args.height)

    image_array = np.zeros((args.height, args.width, 3), dtype=float)
    #create pixel grid
    row_head = camera.top_left_pixel
    for y in range(args.height):
        curr_pixel = row_head
        for x in range(args.width):
            curr_ray = Ray(camera.position, curr_pixel)
            t_min, closest_hit_point, closest_obj = curr_ray.find_ray_closest_intersection(objects)
            if closest_obj is None:
                color = np.array(scene_settings.background_color)
            else:
                color = np.array(compute_color(curr_ray, objects, materials, camera, scene_settings))

            image_array[y, x] = np.clip(color, 0, 1)
            curr_pixel = curr_pixel + camera.pixel_size * camera.width_v
        row_head = row_head + camera.pixel_size * camera.height_v

    save_image(image_array, args.output_image)


if __name__ == '__main__':
    main()

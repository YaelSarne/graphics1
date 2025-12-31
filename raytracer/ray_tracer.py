import argparse
from PIL import Image
import numpy as np
import random
from tqdm import tqdm

from camera import Camera
from light import Light
from material import Material
from scene_settings import SceneSettings
from surfaces.cube import Cube
from surfaces.infinite_plane import InfinitePlane
from surfaces.sphere import Sphere
from ray import Ray
import time

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
                materials.append(material)
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
    return camera, scene_settings, objects, materials


def save_image(image_array, output_filename):
    final_image = np.clip(image_array * 255, 0, 255).astype(np.uint8)
    image = Image.fromarray(final_image)
    image.save(output_filename)


def get_color(scene_settings, ray, lights, materials, objects, camera, max_iters):
    if max_iters <= 0:
        return np.array(scene_settings.background_color)

    t_min, hit_point, obj = ray.find_ray_closest_intersection(objects)
    if obj is None:
        return np.array(scene_settings.background_color)
        
    material = materials[obj.material_index - 1]

    normal = obj.get_normal_from_hit_point(hit_point)
    
    if np.dot(normal, ray.V) > 0:
        normal = -normal
    
    current_color = np.array(color_by_lights(hit_point, normal, lights, objects, material, scene_settings, materials, ray))

    # Transparency
    if material.transparency > 0:
        eps = 1e-4
        new_origin = hit_point + (ray.V * eps)
        
        behind_ray = Ray(new_origin, new_origin + ray.V)
        behind_color = get_color(scene_settings, behind_ray, lights, materials, objects, camera, max_iters - 1)
        
        current_color = material.transparency * behind_color + (1 - material.transparency)*current_color

    # Reflection
    reflection_color = np.array(material.reflection_color)
    if np.any(reflection_color > 0):
        reflection_dir = ray.V - 2 * np.dot(ray.V, normal) * normal
        reflection_dir = reflection_dir / np.linalg.norm(reflection_dir)
        
        eps = 1e-4
        reflected_ray = Ray(hit_point + eps * normal, hit_point + eps * normal + reflection_dir)
        reflection_color_val = get_color(scene_settings, reflected_ray, lights, materials, objects, camera, max_iters - 1)

        current_color = current_color + (reflection_color * reflection_color_val)

    return current_color


def get_light_plane_axes(light_dir):
    light_dir = light_dir / np.linalg.norm(light_dir)
    
    if abs(light_dir[0]) < 0.1 and abs(light_dir[2]) < 0.1:
        helper_vec = np.array([1.0, 0.0, 0.0]) 
    else:
        helper_vec = np.array([0.0, 1.0, 0.0]) 
        
    U = np.cross(helper_vec, light_dir)
    U = U / np.linalg.norm(U)

    V = np.cross(light_dir, U)
    V = V / np.linalg.norm(V)

    return U, V


def color_by_lights(closest_hit_point, normal, lights, objects, material, scene_settings, materials,ray):
    eps = 1e-4
    colors = np.array([0.0, 0.0, 0.0])

    observer_v = -ray.V 

    for light in lights:
        direction_for_grid = closest_hit_point - light.position
        right, up = get_light_plane_axes(direction_for_grid)

        N = int(scene_settings.root_number_shadow_rays)
        
        grid_width = light.radius
        cell_size = grid_width / N
        top_left = light.position - (grid_width / 2.0 * right) - (grid_width / 2.0 * up)
        total_light_received = 0.0
        total_rays = N * N

        for i in range(N):
            for j in range(N):
                current_u = (i + random.random()) * cell_size
                current_v = (j + random.random()) * cell_size
                
                point_on_grid = top_left + (current_u * right) + (current_v * up)
                light_vec = point_on_grid - closest_hit_point
                dist_to_light = np.linalg.norm(light_vec)
                to_light_dir = light_vec / dist_to_light
                shadow_origin = closest_hit_point + (eps * to_light_dir)
                shadow_ray = Ray(shadow_origin, point_on_grid)
                intensity = shadow_ray.visible_factor(objects, dist_to_light, materials)
                total_light_received += intensity

        hit_ratio = total_light_received / total_rays
        light_intensity = (1 - light.shadow_intensity) + light.shadow_intensity * hit_ratio
        if light_intensity > 0:
            light_vec = light.position - closest_hit_point
            light_dir = light_vec / np.linalg.norm(light_vec)

            # Diffuse
            diff_angle = max(0.0, np.dot(normal, light_dir))
            diffuse_light = np.array(light.color) * np.array(material.diffuse_color) * diff_angle 

            # Specular
            reflected_ray_dir = 2 * np.dot(light_dir, normal) * normal - light_dir
            spec_angle = max(0.0, np.dot(reflected_ray_dir, observer_v))
            specular_light = np.array(light.color) * np.array(material.specular_color) * (spec_angle ** material.shininess) * light.specular_intensity
            
            colors += light_intensity * (diffuse_light + specular_light)
        
    return colors


def create_light_list(objects):
    lights = []
    for obj in objects:
        if isinstance(obj, Light):
            lights.append(obj)
    return lights


def compute_color(ray, objects, materials, camera, scene_settings, lights):
    return get_color(scene_settings, ray, lights, materials, objects, camera, scene_settings.max_recursions)


def main():
    parser = argparse.ArgumentParser(description='Python Ray Tracer')
    parser.add_argument('scene_file', type=str, help='Path to the scene file')
    parser.add_argument('output_image', type=str, help='Name of the output image file')
    parser.add_argument('--width', type=int, default=500, help='Image width')
    parser.add_argument('--height', type=int, default=500, help='Image height')
    args = parser.parse_args()

    camera, scene_settings, objects, materials = parse_scene_file(args.scene_file, args.width, args.height)
    lights = []
    surfaces = []
    for obj in objects:
        if isinstance(obj, Light):
            lights.append(obj)
        else:
            surfaces.append(obj)

    image_array = np.zeros((args.height, args.width, 3), dtype=float)
    row_head = camera.top_left_pixel
    lights = create_light_list(objects)
    
    #delete
    start_time = time.time()

    for y in tqdm(range(args.height), desc="Rendering"):
        curr_pixel = row_head
        for x in range(args.width):
            curr_ray = Ray(camera.position, curr_pixel)
            color = np.array(compute_color(curr_ray, surfaces, materials, camera, scene_settings, lights))

            image_array[y, x] = np.clip(color, 0, 1)
            curr_pixel = curr_pixel + camera.pixel_size * camera.width_v
        row_head = row_head - camera.pixel_size * camera.height_v

    save_image(image_array, args.output_image)

    #print to delete:
    end_time = time.time()
    print(f"Finished rendering in {end_time - start_time:.4f} seconds.")


if __name__ == '__main__':
    main()

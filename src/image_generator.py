import os
import random
from PIL import Image, ImageDraw

def get_file_paths(directory):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

def calc_positions(bg, obj, objects):
    # if not objects:
    x = random.randint(0, bg.width - obj.width)
    y = random.randint(0, bg.height - obj.height)

    return {'x': x, 'y': y}

def draw_red_circle(draw, object, radius, x, y, bounds_scale, width):
    center_x = x + (object.width // 2)
    center_y = y + (object.height // 2)

    offset_x = random.randint(-1 * object.width // bounds_scale, object.width // bounds_scale)
    offset_y = random.randint(-1 * object.height // bounds_scale, object.height // bounds_scale)

    draw.ellipse(
        [(center_x - radius + offset_x, center_y - radius + offset_y),
            (center_x + radius + offset_x, center_y + radius + offset_y)],
        outline="red",
        width=width
    )

def insert_object(bg, path, objects, is_deathstar=False):
    object = Image.open(path).convert("RGBA")

    # Apply random transformations
    angle = random.randint(0, 360)
    scale_factor = random.uniform(0.4, 0.7)  # Scale between 30% to 100%
    
    object = object.rotate(angle, expand=True)  # Rotate
    new_size = (int(bg.width * scale_factor), int(bg.height * scale_factor))
    object = object.resize(new_size, Image.LANCZOS)  # Resize

    # Get random position ensuring it stays within bounds
    location = calc_positions(bg, object, objects)
    pos_x = location['x']
    pos_y = location['y']

    # Paste the foreground image on the background
    bg.paste(object, (pos_x, pos_y), object)  # Use fg as a mask to keep transparency

    if is_deathstar:
        draw = ImageDraw.Draw(bg)
        circle_radius = 35
        bounds_scale = 3.5
        c_width = 5
        draw_red_circle(draw, object, circle_radius, pos_x, pos_y, bounds_scale, c_width)

    dims = {'size': object.size, 'x': pos_x, 'y': pos_y}
    return dims

def create_image(name, bg):
    # Select a random background
    objects = []
    
    ds_num = random.randint(0, len(deathstar) - 1)
    ds_path = deathstar[ds_num]
    ds = insert_object(bg, ds_path, objects, True)
    objects.append(ds)

    is_moon = random.randint(0, 1)
    if is_moon:
        moon_select = random.randint(0, len(moon) - 1)
        moon_path = moon[moon_select]
        mn = insert_object(bg, moon_path, objects)
        objects.append(mn)
    else:
        ship_select = random.randint(0, len(spaceship) - 1)
        ship_path = spaceship[ship_select]
        sp = insert_object(bg, ship_path, objects)
        objects.append(sp)
    

def create_dataset(num_images, output_directory, backgrounds):

    for i in range(num_images):
        bg_path = random.choice(backgrounds)
        bg = Image.open(bg_path).convert("RGBA")  # Keep transparency if applicable
        img_name = "deathstar_" + str(random.randint(0, 1000)) + ".png"
        create_image(img_name, bg)
        output_path = os.path.join(output_directory, img_name)
        bg.save(output_path, "PNG")
        print(f"Image saved to {output_path}")

    
output_path = "..\\assets\\image_generation\\output\\"
os.makedirs(output_path, exist_ok=True)

background_path = "..\\assets\\image_generation\\background\\"
deathstar_path = "..\\assets\\image_generation\\deathstar\\"
moon_path = "..\\assets\\image_generation\\moon\\"
spaceship_path = "..\\assets\\image_generation\\spaceship\\"

backgrounds = get_file_paths(background_path)
deathstar = get_file_paths(deathstar_path)
moon = get_file_paths(moon_path)
spaceship = get_file_paths(spaceship_path)

create_dataset(10, output_path, backgrounds)
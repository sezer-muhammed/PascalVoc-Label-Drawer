import os
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
import argparse
import time
import hashlib

def hash_label_to_color(label_name):
    """ Hash the label name to a unique color """
    label_name = label_name.encode()
    color = hashlib.sha1(label_name).hexdigest()[:6]
    color = tuple(int(color[i:i+2], 16) for i in (0, 2 ,4)) + (60,)
    return color

parser = argparse.ArgumentParser(description='Draw labels on images and save them')
parser.add_argument('--images_folder', type=str, help='Path to the folder containing the images', required=True)
parser.add_argument('--annotations_folder', type=str, help='Path to the folder containing the xml annotations', required=True)
parser.add_argument('--output_folder', type=str, help='Path to the folder where the labeled images will be saved', required=True)
parser.add_argument('--overlay', action='store_true', help='Draw labels as overlay on the image')
parser.add_argument('--font_size', type=int, default=20, help='Font size for the labels')
args = parser.parse_args()

images_folder = args.images_folder
annotations_folder = args.annotations_folder
output_folder = args.output_folder
overlay = args.overlay
font_size = args.font_size

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

color_dict = {'tasit': (255, 110, 0, 40), 'insan': (0, 255, 110, 40), 'object3': (0, 0, 255, 40)}

start_time = time.time()
count = 0

# Pre-allocate the image and draw objects
font = ImageFont.truetype("arial.ttf", font_size)

for image_file in os.listdir(images_folder):
    print(f"Processing image: {image_file}", end="\r")
    if image_file.endswith('.jpg') or image_file.endswith('.png'):
        annotation_file = os.path.splitext(image_file)[0] + '.xml'
        annotation_path = os.path.join(annotations_folder, annotation_file)
        if os.path.exists(annotation_path):
            # Open image
            im = Image.open(os.path.join(images_folder, image_file))
            im = im.convert("RGBA")

            # Clear the previous image from the polygon layer
            polygon_layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
            polygon_draw = ImageDraw.Draw(polygon_layer)

            # Open annotation
            tree = ET.parse(annotation_path)
            root = tree.getroot()

            for obj in root.iter('object'):
                name = obj.find('name').text
                xmin = int(obj.find('bndbox/xmin').text)
                ymin = int(obj.find('bndbox/ymin').text)
                xmax = int(obj.find('bndbox/xmax').text)
                ymax = int(obj.find('bndbox/ymax').text)

                if overlay:
                    color = hash_label_to_color(name)
                    points = [(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)]
                    polygon_draw.polygon(points, fill=color)
                    polygon_draw.text((xmin, ymin - 25), name, fill=color, font=font)
                else:
                    color = hash_label_to_color(name)
                    polygon_draw.rectangle((xmin, ymin, xmax, ymax), outline=color, width=5)
                    polygon_draw.text((xmin, ymin - 25), name, fill=color, font=font)
                    
            # Save image
            im = Image.alpha_composite(im, polygon_layer)
            im.save(os.path.join(output_folder, image_file.replace(".jpg", ".png")), "PNG")
            count += 1

    if time.time() - start_time >= 1:
        print(f"Saved {count} images in the last second")
        start_time = time.time()
        count = 0

# Print the final count of images saved
print(f"Saved {count} images in total.")



import os
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
import argparse
import time
import hashlib
import concurrent.futures

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

start_time = time.time()
count = 0

# Pre-allocate the image and draw objects
font = ImageFont.truetype("arial.ttf", font_size)

def process_image(image_file):
    """ Process a single image """
    global count
    global start_time

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
        output_path = os.path.join(output_folder, os.path.basename(image_file).replace(".jpg", ".png"))
        if os.access(output_folder, os.W_OK):
            im.save(output_path, "PNG")
            count += 1
            print(f'{int(count / (time.time() - start_time))} frames saved per second', end="\r")
        else:
            pass

with concurrent.futures.ThreadPoolExecutor() as executor:
    image_files = [os.path.join(images_folder, file) for file in os.listdir(images_folder) if file.endswith('.jpg') or file.endswith('.png')]
    results = [executor.submit(process_image, image_file) for image_file in image_files]



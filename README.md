## Overview
This code provides a way to draw labels on images using the information from the corresponding xml annotations. The labels are drawn as either an overlay on the image or as a rectangle around the object. The labels are also colored based on their name, so that different labels will have different colors, but the same labels will have the same color. The labeled images are saved in a specified output folder.

## Usage


```terminal
python label_images.py --images_folder path/to/images --annotations_folder path/to/annotations --output_folder path/to/output
```


## Arguments
* `images_folder`: Path to the folder containing the images. Required.
* `annotations_folder`: Path to the folder containing the xml annotations. Required.
* `output_folder`: Path to the folder where the labeled images will be saved. Required.
* `overlay`: Draw labels as overlay on the image. Optional.
* `font_size`: Font size for the labels. Optional, default is 20.

# Future Work

- Adding support for other annotation formats such as COCO and VOC
- Implementing more advanced image processing techniques to improve the visualization of labels
- Incorporating more options for label styling (e.g. label background, border, etc.)
- Incorporating support for video data
- Improving performance by implementing parallel processing

# Contribution

If you are interested in contributing to the project, please feel free to open a pull request. We appreciate your help in making this project better.

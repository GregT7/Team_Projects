import cv2
import config
import numpy as np
from matplotlib import pyplot as plt
import image_classifier as clf
from image_classifier import get_file_paths



path = "../assets/test_cases/test_case50.134/images/"
paths = get_file_paths(path)
# file_name = "image9.png"
# file_path = path + file_name

images = []
for image_path in paths:

    image = cv2.imread(image_path)
    red_px = clf.isolate_red_pixels(image, config.params['red'])

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    rows = gray.shape[0]

    # my parameters
    circles = cv2.HoughCircles(red_px, cv2.HOUGH_GRADIENT, dp=config.params['circles']['dp'], minDist=config.params['circles']['minDist'],
                            param1=config.params['circles']['param1'], param2=config.params['circles']['param2'], 
                            minRadius=config.params['circles']['minRadius'], maxRadius=config.params['circles']['maxRadius'])

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            radius = i[2]
            # color = (100, 100, 100)
            color = (255, 0, 255)
            cv2.circle(image, center, radius,color, 3)
    
    images.append(image)

fig, axes = plt.subplots(4, 3, figsize=(15, 5))

for i, image in enumerate(images):
    
    axes[i].imshow(image)
    axes[i].set_title(f"image {i}")
    axes[i].axis('off')
plt.show()

# # Create a figure and a grid of subplots
# fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(10, 5))

# # Plot each image in a subplot
# axes[0].imshow(image1)
# axes[0].set_title('Image 1')
# axes[1].imshow(image2)
# axes[1].set_title('Image 2')
# axes[2].imshow(image3)
# axes[2].set_title('Image 3')

# # Adjust layout and display the plot
# plt.tight_layout()
# plt.show()
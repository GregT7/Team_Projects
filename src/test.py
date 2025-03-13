import cv2
import config
import numpy as np
from matplotlib import pyplot as plt
import image_classifier as clf
from image_classifier import get_file_paths

def draw_circles(image, circles):
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            radius = i[2]
            color = (255, 0, 255)
            cv2.circle(image, center, radius,color, 3)

def crop_circles(image, circles, default_img):
    cropped_images = np.array([])
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            radius = i[2]
            x1 = max(0, center[0] - radius)
            x2 = max(0, center[0] + radius)
            y1 = max(0, center[1] - radius)
            y2 = max(0, center[1] + radius)

        # images_concat = np.concatenate([image1[np.newaxis, :], image2[np.newaxis, :]], axis=0)
            mask = np.zeros((y2-y1, x2-x1), dtype=np.uint8)
            cv2.circle(mask, (radius, radius), radius, 255, -1)
            cropped_circle = cv2.bitwise_and(image[y1:y2, x1:x2], image[y1:y2, x1:x2], mask=mask)
            cropped_images = np.concatenate([cropped_images[np.newaxis, :], cropped_circle[np.newaxis, :]], axis=0)
            # cropped_images.append(cropped_circle)
    else:
        cropped_images = np.append(cropped_images, default_img)

    return cropped_images


def plot_circles(images):
    fig, axes = plt.subplots(2, 5, figsize=(15, 5))


    for i, image in enumerate(images):
        row = int(i / 5)
        col = i % 5
        axes[row][col].imshow(image)
        axes[row][col].set_title(f"image {i}")
        axes[row][col].axis('off')
    plt.show()

path = "../assets/test_cases/test_case50.11234/images/"
output_path = "../assets/test_cases/test_case50.11234/output/"
error_path = "../assets/all_images/other/error.png"
paths = get_file_paths(path)
error_image = cv2.imread(error_path)
images = []
for image_path in paths:
    image = cv2.imread(image_path)
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    red_px = clf.isolate_red_pixels(image, config.params['red'])

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    rows = gray.shape[0]

    # my parameters
    circles = cv2.HoughCircles(red_px, cv2.HOUGH_GRADIENT, dp=config.params['circles']['dp'], minDist=config.params['circles']['minDist'],
                            param1=config.params['circles']['param1'], param2=config.params['circles']['param2'], 
                            minRadius=15, maxRadius=config.params['circles']['maxRadius'])
    
    cropped_images = crop_circles(image, circles, error_image)
    
    images.append(cropped_images)

plot_circles(images)


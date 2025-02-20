from skimage import io, color
from skimage.feature import hog
import matplotlib.pyplot as plt
import numpy as np
from skimage import exposure
import os
import cv2

# Load the image
def get_file_paths(directory):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths


# path = "C:\\Users\\Grego\\Desktop\\deathstar"
# ds_imgs = get_file_paths(path)


# fig, axs = plt.subplots(2, 3, figsize=(8, 6))
# i = 0
# pos = [[0, 0], [0, 1], [0, 2], [1, 0], [1,1], [1,2]]
# for img_path in ds_imgs:
#     print(img_path)
#     image = io.imread(img_path)
#     if image.shape[-1] == 4:
#         image = image[:, :, :3]  # Remove the alpha channel
    
#     image_gray = color.rgb2gray(image)
#     features, hog_image = hog(image_gray, orientations=9, pixels_per_cell=(8, 8),
#                             cells_per_block=(2, 2), visualize=True)

#     hog_image_eq = exposure.equalize_hist(hog_image)

#     axs[pos[i][0], pos[i][1]].imshow(image_gray * 10000, cmap='gray')
#     i += 1

def isolate_red_pixels(image):
    # Convert to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define red color range
    lower_red1 = np.array([0, 120, 70], dtype="uint8")   # Lower red range
    upper_red1 = np.array([10, 255, 255], dtype="uint8")

    lower_red2 = np.array([170, 120, 70], dtype="uint8")  # Upper red range
    upper_red2 = np.array([180, 255, 255], dtype="uint8")

    # Create masks and combine them
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 + mask2

    # Apply the mask
    result = cv2.bitwise_and(image, image, mask=mask)
    
    return result
   
def extract_red_circles(result):
    gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    rows = gray.shape[0]
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8,
                                param1=100, param2=30,
                                minRadius=1, maxRadius=80)
    if circles is None:
        circles = [[]]
    return circles
    
    


path = "C:\\Users\\Grego\\Desktop\\Spring_2025\\Team_Projects_II\\repo\\assets\\train\\deathstar\\ai_deathstar1212.png"
image = io.imread(path)

# Check if the image has an alpha channel (4 channels)
if image.shape[-1] == 4:
    image = image[:, :, :3]  # Remove the alpha channel

# Convert the image to grayscale
image_gray = color.rgb2gray(image)

# Extract HOG features
features, hog_image = hog(image_gray, orientations=9, pixels_per_cell=(8, 8),
                          cells_per_block=(2, 2), visualize=True)

red_px = isolate_red_pixels(image)

# Plot the original grayscale image and HOG features
# hog_image_eq = exposure.equalize_hist(hog_image)
# plt.figure(figsize=(8, 4))
# plt.subplot(1, 2, 1)
# plt.imshow(red_px, cmap='gray')
# plt.title('Input Image')

# plt.subplot(1, 2, 2)
# plt.imshow(hog_image_eq, cmap='gray')
# plt.title('HOG Features')

# plt.show()

cv2.imshow("asd", image)
cv2.waitKey(0)
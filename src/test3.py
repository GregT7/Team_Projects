# import the necessary packages
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import PCA
from skimage import exposure
from skimage import feature
import os
import numpy as np
import cv2
from matplotlib import pyplot as plt


# Load image
image = cv2.imread("..\\assets\\train\\deathstar\\ai_deathstar1212.png")
# image = cv2.imread("..\\assets\\train\\deathstar\\deathstar2.png")

def isolate_red_pixels(image):
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
    return mask

# Process image
mask = isolate_red_pixels(image)

blurred = cv2.GaussianBlur(mask, (9, 9), 2)

circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                           param1=50, param2=30, minRadius=10, maxRadius=80)

# Draw detected circles
output = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)  # Convert to BGR for visualization
if circles is not None:
    circles = np.uint16(np.around(circles))  # Round and convert to integer
    for circle in circles[0, :]:
        x, y, r = circle
        cv2.circle(output, (x, y), r, (0, 255, 0), 2)  # Green circle outline
        cv2.circle(output, (x, y), 2, (0, 0, 255), 3)  # Red center dot

# Display the result
cv2.imshow("Hough Circles", output)
cv2.waitKey(0)
cv2.destroyAllWindows()


import cv2
import numpy as np
from matplotlib import pyplot as plt

# Load the image
path = "C:\\Users\\Grego\\Desktop\\Spring_2025\\Team_Projects_II\\repo\\assets\\train\\deathstar\\deathstar2.png"
image = cv2.imread(path)

def isolate_red_pixels(image):
    lower_red = np.array([0, 0, 0], dtype = "uint8")
    upper_red= np.array([0, 0, 255], dtype = "uint8")

    mask = cv2.inRange(image, lower_red, upper_red)

    # Apply the mask
    return cv2.bitwise_and(image, image, mask=mask)


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

def calculate_histogram(image, bins=32):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    hist = cv2.calcHist([image], [0, 1, 2], None, [bins, bins, bins], [0, 256, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    return hist




# red_px = isolate_red_pixels(image)

# circles = extract_red_circles(red_px)
# print(circles)





# plt.xlim([0, 256])




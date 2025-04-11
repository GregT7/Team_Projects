import numpy as np
import cv2
import image_classifier as clf
import config as c

imagePath = "../assets/test_cases/test_case21.267/test/deathstar/deathstar_705.png"
cpars = c.params['circles']

image = cv2.imread(imagePath)
image = cv2.resize(image, (1024, 1024))
red_mask = clf.isolate_red_pixels(image, c.params['red'])
blurred = cv2.GaussianBlur(red_mask, cpars['kernel_size'], cpars['stdx'])

circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=cpars['dp'], minDist=cpars['minDist'],
                        param1=cpars['param1'], param2=cpars['param2'], minRadius=cpars['minRadius'], 
                        maxRadius=cpars['maxRadius'])

if circles is not None:
    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        cv2.circle(image, (i[0], i[1]), i[2], (0, 255, 0), 2)  # Green circle
        cv2.circle(image, (i[0], i[1]), 2, (255, 0, 0), 3)  # Blue center

# Display result
# cv2.imshow("Detected Red Circles", red_mask)
cv2.imshow("Detected Red Circles", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
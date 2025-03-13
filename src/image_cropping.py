import cv2
import config
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw
import image_classifier as clf
from image_classifier import get_file_paths



path = "../assets/test_cases/test_case50.11234/images/"
output_path = "../assets/test_cases/test_case50.11234/output/"
paths = get_file_paths(path)

images = {}
for image_path in paths:
    img_name = image_path.split('/')[-1]
    images[img_name] = []

    image = cv2.imread(image_path)
    red_px = clf.isolate_red_pixels(image, config.params['red'])

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    rows = gray.shape[0]

    # my parameters
    circles = cv2.HoughCircles(red_px, cv2.HOUGH_GRADIENT, dp=config.params['circles']['dp'], minDist=config.params['circles']['minDist'],
                            param1=config.params['circles']['param1'], param2=config.params['circles']['param2'], 
                            minRadius=15, maxRadius=config.params['circles']['maxRadius'])

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            x, y, r = i[0], i[1], i[2]
            lx, hx = x - r, x + r
            ly, hy = y - r, y + r

            area_of_interest = image[ly:hy, lx:hx]
            # gray_image = cv2.cvtColor(area_of_interest, cv2.COLOR_BGR2GRAY)

            # create a circular mask
            mask = Image.new('L', [2*r, 2*r], 0)
            draw = ImageDraw.Draw(mask)
            draw.pieslice([(0,0),(2*r-1,2*r-1)],0,360,fill=1)
            mask = np.array(mask)
            
            for row in range(len(mask)):
                for col in range(len(mask[0])):
                    if (mask[row][col] == 0):
                        area_of_interest[row][col] = [0, 0, 0]

            cropped_image = cv2.bitwise_and(area_of_interest, area_of_interest, mask = mask)

            # append to cropped images array
            images[img_name].append(cropped_image)




for image in images:
    name = image.split('.')[0]
    i = 0
    for circle in images[image]:
        name += "_circle" + str(i) + ".png"
        img_path = output_path + name
        cv2.imwrite(img_path, images[image][i])
        i +=1


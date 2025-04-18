import cv2
import config
import numpy as np
from PIL import Image, ImageDraw
import image_classifier as clf
from image_classifier import get_file_paths




def crop_image(image_path):
    # setup + path cleaning
    images = []
    image_path = image_path.replace('\\', '/')
    
    # load in and prep image for processing
    image = cv2.imread(image_path)
    red_px = clf.isolate_red_pixels(image, config.params['red'])
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)


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

            images.append(cropped_image)
    
    img_name = image_path.split('/')[-1].split('.')[0]
    return {'img_name': img_name, 'images': images}

def save_cropped_circles(image_dict, path):

    name = image_dict['img_name']
    for i, circle in enumerate(image_dict['images']):
        new_name = name + "_circle" + str(i) + ".png"
        img_path = path + new_name

        cv2.imwrite(img_path, circle)


# # uncomment code below to get it work on an individual image

# # input_path is the path for an individual .png file
# # output_path is where the cropped image will be saved to
# input_path = "C:/Users/Grego/Desktop/test/input/image9.png"
# output_path = "C:/Users/Grego/Desktop/test/output/"

# # to crop the images, use crop_image(file_path) and save the resulting cropped circles into a variable
# image_dict = crop_image(input_path)

# # to save all images from the cropped circle dictionary created previously, use the save_cropped_image function
# # passing in the image_dict and the path where you want all cropped circles to be saved
# save_cropped_circles(image_dict, output_path)


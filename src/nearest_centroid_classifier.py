# import matplotlib.pyplot as plt
# import cv2 as cv
# import numpy as np
# import os

# def houghCircleTransform():
#     path = "C:\\Users\\Grego\\Desktop\\Spring_2025\\Team_Projects_II\\sample_deathstar\\image9.png"
#     # root = os.getcwd()
#     # imgPath = os.path.join(root, path)
#     # imgPath = os.path.join(root, 'demoImages//tesla.jpg')
#     img = cv.imread(path)
#     # img = cv.imread(imgPath)
#     imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
#     imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

#     imgGray = cv.medianBlur(imgGray, 21)
#     circles = cv.HoughCircles(imgGray, cv.HOUGH_GRADIENT, dp=1, minDist=600, param1=200)
#     circles = np.uint16(np.around(circles))
    
#     for circle in circles[0, :]:
#         # print(circle)
#         cv.circle(imgRGB, (circle[0], circle[1]), circle[2], (255,255,255), 10)
    
#     plt.figure()
#     plt.imshow(imgRGB)
#     plt.show()


# if __name__ == '__main__':
#     houghCircleTransform()

import numpy as np
import cv2 as cv
# C:\Users\Grego\Desktop\Spring_2025\Team_Projects_II\examples\deathstar_img
path = "C:\\Users\\Grego\\Desktop\\Spring_2025\\Team_Projects_II\\examples\\deathstar_img\\image9.png"
img = cv.imread(path, cv.IMREAD_GRAYSCALE)
# assert img is not None, "file could not be read, check with os.path.exists()"
img = cv.medianBlur(img,5)
cimg = cv.cvtColor(img,cv.COLOR_GRAY2BGR)

circles = cv.HoughCircles(img,cv.HOUGH_GRADIENT,1,20,
                            param1=50,param2=30,minRadius=0,maxRadius=0)

circles = np.uint16(np.around(circles))
for i in circles[0,:]:
    # draw the outer circle
    cv.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
    # draw the center of the circle
    cv.circle(cimg,(i[0],i[1]),2,(0,0,255),3)

cv.imshow('detected circles',cimg)
cv.waitKey(0)
cv.destroyAllWindows()
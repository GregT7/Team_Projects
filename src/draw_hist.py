import numpy as np
import config as c
import cv2
import image_classifier as clf
import matplotlib.pyplot as plt

imagePath = "../assets/test_cases/test_case21.267/test/deathstar/deathstar_705.png"

hpars = c.params['hist']
image = cv2.imread(imagePath)
image = cv2.resize(image, (1024, 1024))

hist = clf.calculate_histogram(image, hpars)

colors = ('r', 'g', 'b')
plt.figure(figsize=(10, 5))

for i, color in enumerate(colors):
    hist_channel = cv2.calcHist([image], [i], None, [8], [0, 256])
    plt.plot(hist_channel, color=color, label=f'{color.upper()} Channel')
    plt.fill_between(range(8), hist_channel.flatten(), color=color, alpha=0.3)

plt.title("RGB Histogram")
plt.xlabel("Pixel Value")
plt.ylabel("Frequency")
plt.legend()
plt.show()
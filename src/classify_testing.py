from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from skimage import exposure
from skimage import feature
import os
import numpy as np
import cv2
import image_classifier as clf
import config as c


print("[INFO] extracting features...")
hist_dataset = []
circles_dataset = []
labels = []

train_paths = clf.get_file_paths(c.params['train_path'])
train_paths.sort()

hist_model = KNeighborsClassifier(c.params['n'])
circles_model = KNeighborsClassifier(c.params['n'])

# loop over the image paths in the training set
for imagePath in train_paths:

    # extract image class: deathstar or non-deathstar
    img_class = imagePath.split("/")[-2]
    
    # load image, resize it, and extract parameter data
    image = cv2.imread(imagePath)
    image = cv2.resize(image, (1024, 1024))

    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # hog_data = feature.hog(gray, orientations=c.params['hog']['ornts'], pixels_per_cell=c.params['hog']['ppc'],
    #                 cells_per_block=c.params['hog']['cpb'], transform_sqrt=True, block_norm="L1")
    hist_data = clf.calculate_histogram(image, c.params['hist'])

    red_px = clf.isolate_red_pixels(image, c.params['red'])
    circles_data = clf.extract_red_circles(red_px, c.params['circles'])

    
    hist_dataset.append(hist_data)
    circles_dataset.append(circles_data)
    labels.append(img_class)

scaler_hist = StandardScaler().fit(hist_dataset)
hist_scaled = scaler_hist.transform(hist_dataset)
hist_model.fit(hist_dataset, labels)

scaler_circles = StandardScaler().fit(circles_dataset)
circles_scaled = scaler_circles.transform(circles_dataset)
circles_model.fit(circles_dataset, labels)

# tpath = "../assets/test_cases/test_case21.245/test/"
tpath = "../assets/test_cases/test_case21.267/test/"
# tpath = "../assets/test_cases/test_case_X/"
test_paths = clf.get_file_paths(tpath)


print(f"[INFO] evaluating {len(test_paths)} test images...")

# loop over the test dataset
i = 0
total_deathstar = total_nondeathstar = 0
correct_deathstar = correct_nondeathstar = 0

circles_classified = []

for imagePath in test_paths:
    red_px = clf.isolate_red_pixels(image, c.params['red'])
    circles_data = clf.extract_red_circles(red_px, c.params['circles'])
    circles_data = circles_data.transform(circles_data.reshape(1, -1))

    # hist_data = clf.calculate_histogram(image, c.params['hist'])
    # hist_data = scaler_hist.transform(hist_data.reshape(1, -1))
    # scaler_hist.transform(hist_data.reshape(1, -1))



    pred = hist_model.predict(hist_data)

    img_class = imagePath.split("/")[-2]
    if img_class == "deathstar":
        total_deathstar += 1
    elif img_class == "non-deathstar":
        total_nondeathstar += 1

    if (pred == img_class):
        if img_class == "deathstar":
            correct_deathstar += 1
        elif img_class == "non-deathstar":
            correct_nondeathstar += 1

# for imagePath in test_paths:
#     image = cv2.imread(imagePath)
#     image = cv2.resize(image, (1024, 1024))


#     # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     # hog_data = feature.hog(gray, orientations=c.params['hog']['ornts'], pixels_per_cell=c.params['hog']['ppc'],
#     #                 cells_per_block=c.params['hog']['cpb'], transform_sqrt=True, block_norm="L1")
#     # hog_data = scaler_hist.transform(hog_data.reshape(1, -1))
#     hist_data = clf.calculate_histogram(image, c.params['hist'])
#     hist_data = scaler_hist.transform(hist_data.reshape(1, -1))



#     pred = hist_model.predict(hist_data)

#     img_class = imagePath.split("/")[-2]
#     if img_class == "deathstar":
#         total_deathstar += 1
#     elif img_class == "non-deathstar":
#         total_nondeathstar += 1

#     if (pred == img_class):
#         if img_class == "deathstar":
#             correct_deathstar += 1
#         elif img_class == "non-deathstar":
#             correct_nondeathstar += 1

#     # if pred == "deathstar":
#     #     filename = imagePath.split('/')[-1]
#     #     print(f"DS#{i + 1}: {filename}")
#     #     i += 1

ds = {'total': total_deathstar, 'accurate': correct_deathstar}
nds = {'total': total_nondeathstar, 'accurate': correct_nondeathstar}

ds['inaccurate'] = ds['total'] - ds['accurate']
nds['inaccurate'] = nds['total'] - nds['accurate']

stats = {'ds': ds, 'nds':nds, 'misclassified_images': [], 'time': 0}
clf.print_accuracy(stats['ds'], stats['nds'], stats['time'], stats['misclassified_images'], disp_images=False)
# print(f"Total classified: {i}, Total misclassified: {i - 10}")
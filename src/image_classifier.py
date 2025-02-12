# import the necessary packages
from sklearn.neighbors import KNeighborsClassifier
from skimage import exposure
from skimage import feature
import os
import numpy as np
import cv2

def get_file_paths(directory):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

def display_hogImage(image, hogImage, pred, i):
    hogImage = exposure.rescale_intensity(hogImage, out_range=(0, 255))
    hogImage = hogImage.astype("uint8")
    cv2.imshow("HOG Image #{}".format(i + 1), hogImage)
    cv2.putText(image, pred.title(), (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
		(0, 255, 0), 3)
    cv2.imshow("Test Image #{}".format(i + 1), image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def print_accuracy(total_deathstar, correct_deathstar, total_nondeathstar, correct_nondeathstar):
    ds_inaccurate = total_deathstar - correct_deathstar
    nds_inaccurate = total_nondeathstar - correct_nondeathstar
    
    total_images = total_deathstar + total_nondeathstar
    total_accurate = correct_nondeathstar + correct_deathstar
    total_inaccurate = ds_inaccurate + nds_inaccurate

    print(f"Total Deathstar images: {total_deathstar}, accurate: {correct_deathstar}, inaccurate: {ds_inaccurate}")
    print(f"Total Non-deathstar images: {total_nondeathstar}, accurate: {correct_nondeathstar}, inaccurate: {nds_inaccurate}")
    print(f"Total images: {total_images}, accurate: {total_accurate}, inaccurate: {total_inaccurate}")

    print(f"Deathstar accuracy: {correct_deathstar / total_deathstar * 100}%")
    print(f"Non-deathstar accuracy: {correct_nondeathstar / total_nondeathstar * 100}%")
    print(f"Total accuracy: {(correct_deathstar + correct_nondeathstar) / (total_deathstar + total_nondeathstar) * 100}%")

    if not misclassified_images:
        print("No misclassified images...")
    else:
        print("\nMisclassified Images")
        
        for image in misclassified_images:
            print("\t" + image)
    
# def isolate_red_pixels(image):
#     # Convert to HSV
#     hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

#     # Define the range for red color
#     lower_red = np.array([0, 100, 100])
#     upper_red = np.array([10, 255, 255])
#     mask1 = cv2.inRange(hsv, lower_red, upper_red)

#     lower_red = np.array([170, 100, 100])
#     upper_red = np.array([180, 255, 255])
#     mask2 = cv2.inRange(hsv, lower_red, upper_red)

#     # Combine the masks
#     mask = cv2.bitwise_or(mask1, mask2)

#     # Apply the mask
#     return cv2.bitwise_and(image, image, mask=mask)

# def extract_red_circles(result):
#     gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
#     gray = cv2.medianBlur(gray, 5)
#     rows = gray.shape[0]
#     circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8,
#                                 param1=100, param2=30,
#                                 minRadius=1, maxRadius=30)
#     return circles


# initialize the data matrix and labels
print("[INFO] extracting features...")
data = []
labels = []

train_dir = "..\\assets\\train\\temp\\"
train_paths = get_file_paths(train_dir)
test_dir = "..\\assets\\test\\temp\\"
test_paths = get_file_paths(test_dir)

# train_dir = "..\\assets\\train\\"
# train_paths = get_file_paths(train_dir)
# test_dir = "..\\assets\\test\\"
# test_paths = get_file_paths(test_dir)


# loop over the image paths in the training set
for imagePath in train_paths:
    # extract image class: deathstar or non-deathstar
    img_class = imagePath.split("\\")[-2]
    
    # load the image, convert it to grayscale, and detect edges
    image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    logo = cv2.resize(gray, (1024, 1024))
    H = feature.hog(logo, orientations=9, pixels_per_cell=(10, 10),
                    cells_per_block=(2, 2), transform_sqrt=True, block_norm="L1")
    data.append(H)
    labels.append(img_class)


# "train" the nearest neighbors classifier
print("[INFO] training classifier...")
model = KNeighborsClassifier(n_neighbors=1)
model.fit(data, labels)
print("[INFO] evaluating...")

# loop over the test dataset
i = 0
total_deathstar = total_nondeathstar = 0
correct_deathstar = correct_nondeathstar = 0
misclassified_images = []
for imagePath in test_paths:
    img_class = imagePath.split("\\")[-2]
    image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    logo = cv2.resize(gray, (1024, 1024))
    H = feature.hog(logo, orientations=9, pixels_per_cell=(10, 10),
                                cells_per_block=(2, 2), transform_sqrt=True, block_norm="L1")

    pred = model.predict(H.reshape(1, -1))[0]
    
    if img_class == "deathstar":
        total_deathstar += 1
    elif img_class == "non-deathstar":
        total_nondeathstar += 1

    if (pred == img_class):
        if img_class == "deathstar":
            correct_deathstar += 1
        elif img_class == "non-deathstar":
            correct_nondeathstar += 1
    else:
        misclassified_images.append(imagePath.split("\\")[-1])

    i += 1

print_accuracy(total_deathstar, correct_deathstar, total_nondeathstar, correct_nondeathstar)
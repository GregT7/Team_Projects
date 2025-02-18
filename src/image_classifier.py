# import the necessary packages
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from skimage import exposure
from skimage import feature
import os
import numpy as np
import cv2


ornts = 6 # 9 - detailed, 6 - rough
ppc = (128,128) # (10, 10) - detailed, (128, 128)
cpb = (1,1) # (2, 2) - detailed, (1,1) rough
feature_weights = {'hog': 0, 'circles': 24, 'hist': 1}


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

    # if not misclassified_images:
    #     print("No misclassified images...")
    # else:
    #     print("\nMisclassified Images")
        
    #     for image in misclassified_images:
    #         print("\t" + image)
    
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


def extract_red_circles(mask):
    blurred = cv2.GaussianBlur(mask, (9, 9), 2)

    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                            param1=50, param2=30, minRadius=10, maxRadius=80)

    if circles is None:
        circles = np.array([])

    data = np.array([0,0])
    for i in range(len(circles)):
        data[0] += 1
        data[1] += circles[i][0, 2]
    
    if data[0] != 0:
        data[1] /= data[0]
    
    return data

def calculate_histogram(image, bins=8):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    hist = cv2.calcHist([image], [0, 1, 2], None, [bins, bins, bins], [0, 256, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    return hist

def extract_feature_data(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    H = feature.hog(gray, orientations=ornts, pixels_per_cell=ppc,
                    cells_per_block=cpb, transform_sqrt=True, block_norm="L1")
    
    red_px = isolate_red_pixels(image)
    circles = extract_red_circles(red_px)
    hist = calculate_histogram(image)
    dict = {'hog': H, 'red_px': red_px, 'circles': circles, 'hist': hist}
    return dict

def format_data(data):
    formatted_data = {}
    circles = []
    hog = []
    hist = []

    for i in range(len(data)):
        circles.append(data[i]['circles'])
        hog.append(data[i]['hog'])
        hist.append(data[i]['hist'])
    
    formatted_data['circles'] = circles
    formatted_data['hog'] = hog
    formatted_data['hist'] = hist

    return formatted_data





# initialize the data matrix and labels
print("[INFO] extracting features...")
data = []
labels = []

# train_dir = "..\\assets\\test_cases\\tX\\train\\"
train_dir = "..\\assets\\test_cases\\test_case21.22\\train\\"
train_paths = get_file_paths(train_dir)

# test_dir = "..\\assets\\test_cases\\tX\\test\\"
test_dir = "..\\assets\\test_cases\\test_case21.22\\test\\"
test_paths = get_file_paths(test_dir)


# loop over the image paths in the training set
for imagePath in train_paths:
    # extract image class: deathstar or non-deathstar
    img_class = imagePath.split("\\")[-2]
    
    # load the image, convert it to grayscale, and detect edges
    image = cv2.imread(imagePath)
    image = cv2.resize(image, (1024, 1024))

    feature_data = extract_feature_data(image)

    data.append(feature_data)
    labels.append(img_class)

data = format_data(data)


scaler_circles = StandardScaler().fit(data['circles'])
scaler_hog = StandardScaler().fit(data['hog'])
scaler_hist = StandardScaler().fit(data['hist'])

model = KNeighborsClassifier(n_neighbors=1)

circles_scaled = scaler_circles.transform(data['circles'])
hog_scaled = scaler_hog.transform(data['hog'])
hist_scaled = scaler_hist.transform(data['hist'])

circles_weighted = circles_scaled * feature_weights['circles']
hog_weighted = hog_scaled * feature_weights['hog']
hist_weighted = hist_scaled * feature_weights['hist']

training_data = np.hstack((circles_weighted, hog_weighted, hist_weighted))


# "train" the nearest neighbors classifier
print("[INFO] training classifier...")


model.fit(training_data, labels)
# model.fit(training_data, labels)
print("[INFO] evaluating...")

# loop over the test dataset
i = 0
total_deathstar = total_nondeathstar = 0
correct_deathstar = correct_nondeathstar = 0
misclassified_images = []
for imagePath in test_paths:
    img_class = imagePath.split("\\")[-2]
    image = cv2.imread(imagePath)
    image = cv2.resize(image, (1024, 1024))
    feature_data = extract_feature_data(image)

    hog_data = np.array(feature_data['hog']).reshape(1, -1)
    circles_data = np.array(feature_data['circles']).reshape(1, -1)
    hist_data = np.array(feature_data['hist']).reshape(1, -1)

    test_hog_scaled = scaler_hog.transform(hog_data)
    test_circles_scaled = scaler_circles.transform(circles_data)
    test_hist_scaled = scaler_hist.transform(hist_data)

    test_hog_weighted = test_hog_scaled * feature_weights['hog']
    test_circles_weighted = test_circles_scaled * feature_weights['circles']
    test_hist_weighted = test_hist_scaled * feature_weights['hist']


    fdata = np.hstack((test_circles_weighted, test_hog_weighted, test_hist_weighted))

    
    # pred = model.predict(test_circles_weighted)
    pred = model.predict(fdata)
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
# import the necessary packages
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from skimage import exposure
from skimage import feature
import os
import numpy as np
import cv2
import config

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

def print_accuracy(ds, nds, misclassified_images, disp_images=False):
    total_images = ds['total'] + nds['total']
    total_accurate = nds['accurate'] + ds['accurate']
    total_inaccurate = nds['inaccurate'] + ds['inaccurate']

    print(f"Total Deathstar images: {ds['total']}, accurate: {ds['accurate']}, inaccurate: {ds['inaccurate']}")
    print(f"Total Non-deathstar images: {nds['total']}, accurate: {nds['accurate']}, inaccurate: {nds['inaccurate']}")
    print(f"Total images: {total_images}, accurate: {total_accurate}, inaccurate: {total_inaccurate}")

    print(f"Deathstar accuracy: {ds['accurate'] / ds['total'] * 100}%")
    print(f"Non-deathstar accuracy: {nds['accurate'] / nds['total'] * 100}%")
    print(f"Total accuracy: {(ds['accurate'] + nds['accurate']) / total_images * 100}%")

    if disp_images:
        if not misclassified_images:
            print("No misclassified images...")
        else:
            print("\nMisclassified Images")
            
            for image in misclassified_images:
                print("\t" + image)
    
def isolate_red_pixels(image, ranges=config.redpx_params):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define red color range
    lower_red1 = np.array(ranges['lr1'], dtype="uint8")   # Lower red range
    upper_red1 = np.array(ranges['ur1'], dtype="uint8")

    lower_red2 = np.array(ranges['lr2'], dtype="uint8")  # Upper red range
    upper_red2 = np.array(ranges['ur2'], dtype="uint8")

    # Create masks and combine them
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 + mask2

    return mask


def extract_red_circles(mask, cpars = config.circ_params):
    blurred = cv2.GaussianBlur(mask, cpars['kernel_size'], cpars['stdx'])
    
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=cpars['dp'], minDist=cpars['minDist'],
                            param1=cpars['param1'], param2=cpars['param2'], minRadius=cpars['minRadius'], 
                            maxRadius=cpars['maxRadius'])

    if circles is None:
        circles = np.array([])

    data = np.array([0,0])
    for i in range(len(circles)):
        data[0] += 1
        data[1] += circles[i][0, 2]
    
    if data[0] != 0:
        data[1] /= data[0]
    
    return data

def calculate_histogram(image, hpars=config.hist_params):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    hist = cv2.calcHist([image], hpars['channels'], None, 
                        [hpars['bins'], hpars['bins'], hpars['bins']], hpars['ranges'])
    hist = cv2.normalize(hist, hist).flatten()
    return hist

def extract_feature_data(image, hog=config.hog, rpars = config.redpx_params, 
                         cpars = config.circ_params, hpars=config.hist_params):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    H = feature.hog(gray, orientations=hog['ornts'], pixels_per_cell=hog['ppc'],
                    cells_per_block=hog['cpb'], transform_sqrt=True, block_norm="L1")
    
    red_px = isolate_red_pixels(image, rpars)
    circles = extract_red_circles(red_px, cpars)
    hist = calculate_histogram(image, hpars)
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

def extract_features(train_dir=config.train_dir):
    # initialize the data matrix and labels
    print("[INFO] extracting features...")
    data = []
    labels = []

    train_paths = get_file_paths(train_dir)

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

    return {'data': format_data(data), 'labels': labels}

def train_model(data, labels, n=config.num_neighbors, weights=config.feature_weights):
    scaler_circles = StandardScaler().fit(data['circles'])
    scaler_hog = StandardScaler().fit(data['hog'])
    scaler_hist = StandardScaler().fit(data['hist'])

    model = KNeighborsClassifier(n)

    circles_scaled = scaler_circles.transform(data['circles'])
    hog_scaled = scaler_hog.transform(data['hog'])
    hist_scaled = scaler_hist.transform(data['hist'])

    circles_weighted = circles_scaled * weights['circles']
    hog_weighted = hog_scaled * weights['hog']
    hist_weighted = hist_scaled * weights['hist']

    training_data = np.hstack((circles_weighted, hog_weighted, hist_weighted))

    # "train" the nearest neighbors classifier
    print("[INFO] training classifier...")
    model.fit(training_data, labels)

    kNN = {'model': model, 'scaler_circles': scaler_circles, 'scaler_hog': scaler_hog,
           'scaler_hist': scaler_hist}
    return kNN

def test_model(kNN, test_dir=config.test_dir, weights = config.feature_weights):
    print("[INFO] evaluating...")
    
    # extract the test paths
    test_paths = get_file_paths(test_dir)

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

        fdata = scale_data(feature_data, kNN, weights)

        pred = kNN['model'].predict(fdata)
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

    ds = {'total': total_deathstar, 'accurate': correct_deathstar}
    nds = {'total': total_nondeathstar, 'accurate': correct_nondeathstar}

    ds['inaccurate'] = ds['total'] - ds['accurate']
    nds['inaccurate'] = nds['total'] - nds['accurate']

    stats = {'ds': ds, 'nds':nds, 'misclassified_images': misclassified_images}
    return stats
    # print_accuracy(ds, nds, misclassified_images)

def scale_data(feature_data, kNN, weights=config.feature_weights):
    hog_data = np.array(feature_data['hog']).reshape(1, -1)
    circles_data = np.array(feature_data['circles']).reshape(1, -1)
    hist_data = np.array(feature_data['hist']).reshape(1, -1)

    test_hog_scaled = kNN['scaler_hog'].transform(hog_data)
    test_circles_scaled = kNN['scaler_circles'].transform(circles_data)
    test_hist_scaled = kNN['scaler_hist'].transform(hist_data)

    test_hog_weighted = test_hog_scaled * weights['hog']
    test_circles_weighted = test_circles_scaled * weights['circles']
    test_hist_weighted = test_hist_scaled * weights['hist']

    return np.hstack((test_circles_weighted, test_hog_weighted, test_hist_weighted))
# import the necessary packages
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from skimage import exposure
from skimage import feature
import os
import numpy as np
import cv2
import shutil

def get_file_paths(directory):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            filtered_path = os.path.join(root, file).replace("\\", "/")
            file_paths.append(filtered_path)

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

def print_accuracy(ds, nds, time, misclassified_images=[], disp_images=False):
    total_images = ds['total'] + nds['total']
    total_accurate = nds['accurate'] + ds['accurate']
    total_inaccurate = nds['inaccurate'] + ds['inaccurate']

    print(f"Total Deathstar images: {ds['total']}, accurate: {ds['accurate']}, inaccurate: {ds['inaccurate']}")
    print(f"Total Non-deathstar images: {nds['total']}, accurate: {nds['accurate']}, inaccurate: {nds['inaccurate']}")
    print(f"Total images: {total_images}, accurate: {total_accurate}, inaccurate: {total_inaccurate}")

    try:
        print(f"Deathstar accuracy: {round(ds['accurate'] / ds['total'] * 100, 2)}%")
        print(f"Non-deathstar accuracy: {round(nds['accurate'] / nds['total'] * 100, 2)}%")
        print(f"Total accuracy: {round((ds['accurate'] + nds['accurate']) / total_images * 100, 2)}%")
        print(f"Total time: {time} seconds")
    except:
        print("divide by 0 exception")


    if disp_images:
        if not misclassified_images:
            print("No misclassified images...")
        else:
            print("\nMisclassified Images")
            
            for image in misclassified_images:
                print("\t" + image)
    
def isolate_red_pixels(image, ranges):
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


def extract_red_circles(mask, cpars):
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

def calculate_histogram(image, hpars):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    hist = cv2.calcHist([image], hpars['channels'], None, 
                        [hpars['bins'], hpars['bins'], hpars['bins']], hpars['ranges'])
    hist = cv2.normalize(hist, hist).flatten()
    return hist



def format_data(data, params):
    formatted_data = {}
    circles = []
    hog = []
    hist = []

    for i in range(len(data)):
        if 'hog' in params['fsel']:
            hog.append(data[i]['hog'])

        if 'circles' in params['fsel']:
            circles.append(data[i]['circles'])
        
        if 'hist' in params['fsel']:
            hist.append(data[i]['hist'])
    
    if 'hog' in params['fsel']:
        formatted_data['hog'] = hog
        
    if 'circles' in params['fsel']:
        formatted_data['circles'] = circles
    
    if 'hist' in params['fsel']:
        formatted_data['hist'] = hist

    return formatted_data


def extract_feature_data(image, params):
    dict = {}
    if 'hog' in params['fsel']:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        dict['hog'] = feature.hog(gray, orientations=params['hog']['ornts'], pixels_per_cell=params['hog']['ppc'],
                        cells_per_block=params['hog']['cpb'], transform_sqrt=True, block_norm="L1")
    
    if 'circles' in params['fsel']:
        red_px = isolate_red_pixels(image, params['red'])
        dict['circles'] = extract_red_circles(red_px, params['circles'])

    if 'hist' in params['fsel']:
        dict['hist'] = calculate_histogram(image, params['hist'])

    return dict

def extract_features(params):
    # initialize the data matrix and labels
    print("[INFO] extracting features...")
    data = []
    labels = []

    train_paths = get_file_paths(params['train_path'])
    train_paths.sort()

    # loop over the image paths in the training set
    for imagePath in train_paths:
        # extract image class: deathstar or non-deathstar
        img_class = imagePath.split("/")[-2]
        
        # load image, resize it, and extract parameter data
        image = cv2.imread(imagePath)
        image = cv2.resize(image, (1024, 1024))
        feature_data = extract_feature_data(image, params)

        data.append(feature_data)
        labels.append(img_class)

    return {'data': format_data(data, params), 'labels': labels}


def train_model(data, labels, params):
    model = KNeighborsClassifier(params['n'])
    training_dict = {}
    scalers = {}
    
    if 'hog' in params['fsel']:
        scaler_hog = StandardScaler().fit(data['hog'])
        hog_scaled = scaler_hog.transform(data['hog'])
        training_dict['hog'] = hog_scaled * params['weight']['hog']
        scalers['hog'] = scaler_hog
    
    if 'circles' in params['fsel']:
        scaler_circles = StandardScaler().fit(data['circles'])
        circles_scaled = scaler_circles.transform(data['circles'])
        training_dict['circles'] = circles_scaled.astype(np.float64) * params['weight']['circles']
        scalers['circles'] = scaler_circles

    if 'hist' in params['fsel']:
        scaler_hist = StandardScaler().fit(data['hist'])
        hist_scaled = scaler_hist.transform(data['hist'])
        training_dict['hist'] = hist_scaled * params['weight']['hist']
        scalers['hist'] = scaler_hist
    
    training_data = np.hstack(tuple(training_dict.values()))

    # "train" the nearest neighbors classifier
    print("[INFO] training classifier...")
    model.fit(training_data, labels)
    np.savetxt("training_test.txt", training_data, fmt="%.10f") 
    kNN = {'model': model, 'scalers': scalers}
    return kNN

def test_model(kNN, params, move_files=False):
    print("[INFO] evaluating...")
    
    # extract the test paths
    test_paths = get_file_paths(params['test_path'])

    # loop over the test dataset
    i = 0
    total_deathstar = total_nondeathstar = 0
    correct_deathstar = correct_nondeathstar = 0
    misclassified_images = []
    for imagePath in test_paths:
        img_class = imagePath.split("/")[-2]
        image = cv2.imread(imagePath)
        image = cv2.resize(image, (1024, 1024))
        feature_data = extract_feature_data(image, params)
        scaled_data = scale_data(feature_data, kNN, params)

        pred = kNN['model'].predict(scaled_data)
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
            misclassified_images.append(imagePath.split("/")[-1])

        if move_files and pred == "deathstar":
            filename = "ds" if img_class == "deathstar" else "nds"
            filename += "_" + imagePath.split('/')[-1]
            copy_location = params['out_path'] + filename
            shutil.copy(imagePath, copy_location)
        i += 1

    ds = {'total': total_deathstar, 'accurate': correct_deathstar}
    nds = {'total': total_nondeathstar, 'accurate': correct_nondeathstar}

    ds['inaccurate'] = ds['total'] - ds['accurate']
    nds['inaccurate'] = nds['total'] - nds['accurate']

    stats = {'ds': ds, 'nds':nds, 'misclassified_images': misclassified_images}
    return stats

def scale_data(feature_data, kNN, params):
    data_dict = {}
    if 'hog' in params['fsel']:
        hog_data = np.array(feature_data['hog']).reshape(1, -1)
        test_hog_scaled = kNN['scalers']['hog'].transform(hog_data)
        data_dict['hog'] = test_hog_scaled * params['weight']['hog']
        
    if 'circles' in params['fsel']:
        circles_data = np.array(feature_data['circles']).reshape(1, -1)
        test_circles_scaled = kNN['scalers']['circles'].transform(circles_data)
        data_dict['circles'] = test_circles_scaled.astype(np.float64) * params['weight']['circles']

    if 'hist' in params['fsel']:
        hist_data = np.array(feature_data['hist']).reshape(1, -1)
        test_hist_scaled = kNN['scalers']['hist'].transform(hist_data)
        data_dict['hist'] = test_hist_scaled * params['weight']['hist']

    return np.hstack(tuple(data_dict.values()))

def parse_feature_select(weight):
    fsel = []
    if weight['hog'] > 0:
        fsel.append('hog')
    if weight['circles'] > 0:
        fsel.append('circles')
    if weight['hist'] > 0:
        fsel.append('hist')
    return fsel



def demo_feature_extraction(params):
    print("[INFO] extracting features...")
    hist_dataset = []
    circles_dataset = []
    labels = []

    train_paths = get_file_paths(params['train_path'])
    train_paths.sort()

    # loop over the image paths in the training set
    for imagePath in train_paths:

        # extract image class: deathstar or non-deathstar
        img_class = imagePath.split("/")[-2]
        
        # load image, resize it, and extract parameter data
        image = cv2.imread(imagePath)
        image = cv2.resize(image, (1024, 1024))

        hist_data = calculate_histogram(image, params['hist'])

        red_px = isolate_red_pixels(image, params['red'])
        circles_data = extract_red_circles(red_px, params['circles'])

        
        hist_dataset.append(hist_data)
        circles_dataset.append(circles_data)
        labels.append(img_class)
    return {'hist': hist_dataset, 'circles': circles_dataset, 'labels': labels}

def demo_train_models(params, data):
    hist_model = KNeighborsClassifier(params['n'])
    circles_model = KNeighborsClassifier(params['n'])
    hist_model.fit(data['hist'], data['labels'])
    circles_model.fit(data['circles'], data['labels'])
    return {'hist': hist_model, 'circles': circles_model}

def demo_classify_images(params, models, moveFiles=False):
    test_paths = get_file_paths(params['test_path'])
    print(f"[INFO] evaluating {len(test_paths)} test images...")
    i = 0
    for imagePath in test_paths:
        image = cv2.imread(imagePath)
        image = cv2.resize(image, (1024, 1024))

        hist_data = calculate_histogram(image, params['hist'])
        hist_data = hist_data.reshape(1, -1)

        red_px = isolate_red_pixels(image, params['red'])
        circles_data = extract_red_circles(red_px, params['circles'])
        circles_data = circles_data.reshape(1, -1)

        hist_pred = str(models['hist'].predict(hist_data)[0])
        circles_pred = str(models['circles'].predict(circles_data)[0])

        pred = ""

        if (circles_pred == hist_pred):
            
            if circles_pred == "deathstar":
                pred = "deathstar"
            else:
                pred = "non-deathstar"
        else:
            pred = "non-deathstar"

        if pred == "deathstar":
            i += 1
            filename = imagePath.split('/')[-1]
            print(f"DS#{i}: {filename}")

            if moveFiles:
                copy_location = params['out_path'] + filename
                shutil.copy(imagePath, copy_location)
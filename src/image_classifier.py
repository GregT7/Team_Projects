# import the necessary packages
from sklearn.neighbors import KNeighborsClassifier
from skimage import exposure
from skimage import feature
import os
import cv2

def get_file_paths(directory):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

def display_hogImage(image, hogImage, i):
    hogImage = exposure.rescale_intensity(hogImage, out_range=(0, 255))
    hogImage = hogImage.astype("uint8")
    cv2.imshow("HOG Image #{}".format(i + 1), hogImage)
    cv2.putText(image, pred.title(), (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
		(0, 255, 0), 3)
    cv2.imshow("Test Image #{}".format(i + 1), image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    

# initialize the data matrix and labels
print("[INFO] extracting features...")
data = []
labels = []

train_dir = "..\\assets\\train\\"
train_paths = get_file_paths(train_dir)
test_dir = "..\\assets\\test\\"
test_paths = get_file_paths(test_dir)


# loop over the image paths in the training set
for imagePath in train_paths:
    # extract image class: deathstar or non-deathstar
    make = imagePath.split("\\")[-2]
    
    # load the image, convert it to grayscale, and detect edges
    image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    logo = cv2.resize(gray, (1024, 1024))
    (H, hogImage) = feature.hog(logo, orientations=9, pixels_per_cell=(10, 10),
                    cells_per_block=(2, 2), transform_sqrt=True, block_norm="L1", visualize=True)
    data.append(H)
    labels.append(make)


# "train" the nearest neighbors classifier
print("[INFO] training classifier...")
model = KNeighborsClassifier(n_neighbors=1)
model.fit(data, labels)
print("[INFO] evaluating...")

# loop over the test dataset
i = 0
for imagePath in test_paths:
    image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    logo = cv2.resize(gray, (1024, 1024))
    (H, hogImage) = feature.hog(logo, orientations=9, pixels_per_cell=(10, 10),
                                cells_per_block=(2, 2), transform_sqrt=True, block_norm="L1", visualize=True)
    pred = model.predict(H.reshape(1, -1))[0]
    display_hogImage(image, hogImage, i)
    i += 1
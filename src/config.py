# training/testing paths
train_dir = "..\\assets\\test_cases\\test_case21.22\\train\\"
test_dir = "..\\assets\\test_cases\\test_case21.22\\test\\"

# kNN - number of neighbors
num_neighbors = 1
model = KNeighborsClassifier(n_neighbors=num_neighbors)

# Feature weights
feature_weights = {'hog': 0, 'circles': 24, 'hist': 1}

# Hog Feature Extraction
ornts = 6 
ppc = (128,128)
cpb = (1,1)


# red pixel isolation function
lower_red1 = np.array([0, 120, 70], dtype="uint8")   # Lower red range
upper_red1 = np.array([10, 255, 255], dtype="uint8")
lower_red2 = np.array([170, 120, 70], dtype="uint8")  # Upper red range
upper_red2 = np.array([180, 255, 255], dtype="uint8")


# circle detection
blurred = cv2.GaussianBlur(mask, (9, 9), 2)
circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                        param1=50, param2=30, minRadius=10, maxRadius=80)

# histogram
bins = 8
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
hist = cv2.calcHist([image], [0, 1, 2], None, [bins, bins, bins], [0, 256, 0, 256, 0, 256])
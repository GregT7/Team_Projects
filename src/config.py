# training/testing paths
train_dir = "..\\assets\\test_cases\\test_case21.22\\train\\"
test_dir = "..\\assets\\test_cases\\test_case21.22\\test\\"

# kNN - number of neighbors
num_neighbors = 1

# Feature weights
feature_weights = {'hog': 0, 'circles': 24, 'hist': 1}

# Hog Feature Extraction
ornts = 6 
ppc = (128,128)
cpb = (1,1)

# red pixel isolation function
low_r1 = [0, 120, 70]
up_r1 = [10, 255, 255]
low_r2 = [170, 120, 70]
up_r2 = [180, 255, 255]

# circle detection - Gaussian Blur
kernel_size = (9, 9)
std_x = 2

# circle detection - Hough Circle Transform
dp = 1.2
minDist = 20
param1 = 50
param2 = 30
minRadius = 10
maxRadius = 80

# histogram
bins = 8
channels = [0, 1, 2]
ranges = [0, 256, 0, 256, 0, 256]
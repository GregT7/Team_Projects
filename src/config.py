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
hog_params = {'ornts': ornts, 'ppc': ppc, 'cpb': cpb}

# red pixel isolation function
low_r1 = [0, 120, 70]
up_r1 = [10, 255, 255]
low_r2 = [170, 120, 70]
up_r2 = [180, 255, 255]
redpx_params = {'lr1': low_r1, 'lr2': low_r2, 'ur1': up_r1, 'ur2': up_r2}

# circle detection - Gaussian Blur
kernel_size = (9, 9)
stdx = 2
circ_params = {'kernel_size': kernel_size, 'stdx': stdx}

# circle detection - Hough Circle Transform
dp = 1.2
minDist = 20
param1 = 50
param2 = 30
minRadius = 10
maxRadius = 80
circ_params.update({'dp': dp, 'minDist': minDist, 'param1': param1, 'param2': param2, 
               'minRadius': minRadius, 'maxRadius': maxRadius})

# histogram
bins = 8
channels = [0, 1, 2]
ranges = [0, 256, 0, 256, 0, 256]
hist_params = {'bins': bins, 'channels': channels, 'ranges': ranges}

params = {'train_path': train_dir, 'test_path': test_dir, 'hist': hist_params, 'circle': circ_params, 
            'red': redpx_params, 'hog': hog_params, 'weight': feature_weights, 'n': num_neighbors}
import image_classifier as clf

# def extract_feature_data(image, hog=config.hog, rpars = config.redpx_params, 
#                          cpars = config.circ_params, hpars=config.hist_params):
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     H = feature.hog(gray, orientations=hog['ornts'], pixels_per_cell=hog['ppc'],
#                     cells_per_block=hog['cpb'], transform_sqrt=True, block_norm="L1")
    
#     red_px = isolate_red_pixels(image, rpars)
#     circles = extract_red_circles(red_px, cpars)
#     hist = calculate_histogram(image, hpars)
#     dict = {'hog': H, 'red_px': red_px, 'circles': circles, 'hist': hist}
#     return dict


p1 = "..\\assets\\test_cases\\test_case21.22\\train\\"
p2 = "..\\assets\\train\\"
train_dirs = [p1, p2]

p1 = "..\\assets\\test_cases\\test_case21.22\\test\\"
p2 ="..\\assets\\train\\"
test_dirs = [p1, p2]

w1 = {'hog': 0, 'circles': 24, 'hist': 1}
w2 = {'hog': 0, 'circles': 24, 'hist': 0.5}
weights = [w1, w2]

num_neigbors1 = 1
n = [num_neigbors1, num_neigbors1]


hg1 = {'ornts': 6, 'ppc': (128, 128), 'cpb': (1,1)}
hg2 = {'ornts': 6, 'ppc': (64, 64), 'cpb': (1,1)}
hogs = [hg1, hg2]

low_r1 = [0, 120, 70]
up_r1 = [10, 255, 255]
low_r2 = [170, 120, 70]
up_r2 = [180, 255, 255]
r1 = {'lr1': low_r1, 'lr2': low_r2, 'ur1': up_r1, 'ur2': up_r2}
rs = [r1, r1]

c1 = {'kernel_size': (9, 9), 'stdx': 2}
c1.update({'dp': 1.2, 'minDist': 20, 'param1': 50, 'param2': 30, 
               'minRadius': 10, 'maxRadius': 80})

circles = [c1, c1]

hs1 = {'bins': 8, 'channels': [0, 1, 2], 'ranges': [0, 256, 0, 256, 0, 256]}
hist = [hs1, hs1]

num_rounds = len(train_dirs)
for i in range(num_rounds):
    params = {'train_path': train_dirs[i], 'test_path': test_dirs[i], 'hist': hist[i], 'circle': circles[i], 
              'red': rs[i], 'hog': hogs[i], 'weight': weights[i], 'n': n[i]}
              
    features = clf.extract_features(params)
    kNN = clf.train_model(features['data'], features['labels'], params)
    stats = clf.test_model(kNN, params)
    clf.print_accuracy(stats['ds'], stats['nds'], stats['misclassified_images'])



print("done")


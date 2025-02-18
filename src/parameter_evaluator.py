import image_classifier as clf

p1 = "..\\assets\\test_cases\\test_case21.22\\train\\"
p2 = "..\\assets\\test_cases\\test_case21.245\\train\\"
train_dirs = [p1, p2]

p1 = "..\\assets\\test_cases\\test_case21.22\\test\\"
p2 ="..\\assets\\test_cases\\test_case21.245\\test\\"
test_dirs = [p1, p2]

fsel1 = ['hog', 'hist']
fsel2 = ['hist', 'circles']
feature_select = [fsel1, fsel2]

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
for i in range(1):
    params = {'train_path': train_dirs[i], 'test_path': test_dirs[i], 'hist': hist[i], 'circles': circles[i], 
              'red': rs[i], 'hog': hogs[i], 'weight': weights[i], 'n': n[i], 'fsel': feature_select[i]}
              
    features = clf.extract_features(params)
    kNN = clf.train_model(features['data'], features['labels'], params)
    stats = clf.test_model(kNN, params)
    clf.print_accuracy(stats['ds'], stats['nds'], stats['misclassified_images'])



print("done")


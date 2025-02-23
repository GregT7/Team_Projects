import image_classifier as clf
import time
import config

start = time.time()
features = clf.extract_features(config.params)
kNN = clf.train_model(features['data'], features['labels'], config.params)
stats = clf.test_model(kNN, config.params, move_files=True)
stats['time'] = round(time.time() - start, 2)
clf.print_accuracy(stats['ds'], stats['nds'], stats['time'], stats['misclassified_images'], disp_images=True)
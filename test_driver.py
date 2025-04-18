import image_classifier as clf
import time
import config

if __name__ == '__main__':
    start = time.time()
    features = clf.extract_features(config.params)
    kNN = clf.train_model(features['data'], features['labels'], config.params)
    stats = clf.test_model(kNN, config.params, move_files=False) # change to True to move classified files
    stats['time'] = round(time.time() - start, 2)
    clf.print_accuracy(stats['ds'], stats['nds'], stats['time'], stats['misclassified_images'], disp_images=True)
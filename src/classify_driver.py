import image_classifier as clf
import config

if __name__ == '__main__':
    features = clf.extract_features(config.params)
    kNN = clf.train_model(features['data'], features['labels'], config.params)
    stats = clf.test_model(kNN, config.params)
    clf.print_accuracy(stats['ds'], stats['nds'], stats['misclassified_images'])
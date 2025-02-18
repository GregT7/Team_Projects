import image_classifier as clf
import config as c

if __name__ == '__main__':
    features = clf.extract_features()
    kNN = clf.train_model(features['data'], features['labels'])
    stats = clf.test_model(kNN)
    clf.print_accuracy(stats['ds'], stats['nds'], stats['misclassified_images'])
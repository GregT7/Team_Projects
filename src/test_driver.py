import image_classifier as clf
import time
import config

if __name__ == '__main__':
    start = time.time()
    training_data = clf.demo_feature_extraction(config.params)
    models = clf.demo_train_models(config.params, training_data)
    stats = clf.test_classify_images(config.params, models, moveFiles=False)
    stats['time'] = round(time.time() - start, 2)
    clf.print_accuracy(stats['ds'], stats['nds'], stats['time'], stats['misclassified_images'], disp_images=True)
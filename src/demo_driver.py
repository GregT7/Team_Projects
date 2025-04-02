import image_classifier as clf
import config

if __name__ == '__main__':
    training_data = clf.demo_feature_extraction(config.params)
    models = clf.demo_train_models(config.params, training_data)
    clf.demo_classify_images(config.params, models, moveFiles=True)
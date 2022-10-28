from sklearn.ensemble import RandomForestClassifier
import joblib
from sklearn import metrics
import numpy as np
import argparse
import logging
import os


def train(args):
    with np.load(args.data_file) as data:
        train_examples = data['x_train']
        train_labels = data['y_train']
        test_examples = data['x_test']
        test_labels = data['y_test']
    
    input_shape = (-1, 784)
    train_examples = train_examples.reshape(input_shape)
    test_examples = test_examples.reshape(input_shape)

    classifier = RandomForestClassifier(n_estimators=args.n_estimators)
    classifier.fit(train_examples, train_labels)

    train_preds = classifier.predict(train_examples)
    print("Train report %s:\n%s\n"
          % (classifier, metrics.classification_report(train_labels, train_preds)))
    print("Train confusion matrix:\n%s" % metrics.confusion_matrix(train_labels, train_preds))

    test_preds = classifier.predict(test_examples)
    print("Test report %s:\n%s\n"
          % (classifier, metrics.classification_report(test_labels, test_preds)))
    print("Test confusion matrix:\n%s" % metrics.confusion_matrix(test_labels, test_preds))

    model_path = os.path.join(args.saved_model_path, 'sk_mnist.pkl')
    print("Save model to {}".format(model_path))
    joblib.dump(classifier, model_path)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--n_estimators',
                        type=int,
                        required=True,
                        help='Number of estimators.')
    parser.add_argument('--saved_model_path',
                        type=str,
                        required=True,
                        help='Model export directory.')
    parser.add_argument('--data_file',
                        type=str,
                        required=True,
                        help='Data file to train and test.')
    args = parser.parse_args()
    train(args)

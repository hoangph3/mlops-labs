# Original source code and more details can be found in:
# https://scikit-learn.org/stable/auto_examples/classification/plot_digits_classification.html

# Import datasets, classifiers and performance metrics
from sklearn import datasets, svm, metrics
from sklearn.model_selection import train_test_split
import joblib
import os

# The digits dataset
digits = datasets.load_digits()

# To apply a classifier on this data, we need to flatten the image, to
# turn the data in a (samples, feature) matrix:
n_samples = len(digits.images)
data = digits.images.reshape((n_samples, -1))

# Create a classifier: a support vector classifier
classifier = svm.SVC(gamma=0.001, verbose=2)

# Split data into train and test subsets
X_train, X_test_digits, y_train, y_test_digits = train_test_split(
    data, digits.target, test_size=0.3, shuffle=False)

# We learn the digits on the first half of the digits
classifier.fit(X_train, y_train)

# Save model
mnist_svm_path = "models/mnist_sklearn"
os.makedirs(mnist_svm_path, exist_ok=True)

mnist_svm_model_path = os.path.join(mnist_svm_path, "model.joblib")
joblib.dump(classifier, mnist_svm_model_path)

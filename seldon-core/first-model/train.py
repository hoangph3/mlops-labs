from sklearn import datasets
from sklearn import svm
import pickle

# Load the Iris dataset
iris = datasets.load_iris()

# Train a classifier
classifier = svm.SVC(verbose=2)
classifier.fit(iris.data, iris.target)

# Export the classifier to a file

with open('model.pkl', 'wb') as model_file:
    pickle.dump(classifier, model_file)
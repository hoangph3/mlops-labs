import pickle
from sklearn import svm

class IrisClassifier:
    def __init__(self):
        self._model: svm.SVC = pickle.load(open("model.pkl", "rb"))

    def predict(self, X, features_names=None, meta=None):
        output = self._model.predict(X)
        return output

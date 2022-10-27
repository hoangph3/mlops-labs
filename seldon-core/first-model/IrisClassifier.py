import pickle

class IrisClassifier:
    def __init__(self):
        self._model = pickle.load(open("model.pkl", "rb"))

    def predict(self, X, features_names=None, meta=None):
        output = self._model(X)
        return output

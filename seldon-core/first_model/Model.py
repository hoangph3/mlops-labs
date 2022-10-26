import pickle
class Model:
    def __init__(self):
        self._model = pickle.loads(open("model.pkl", "rb"))

    def predict(self, X):
        output = self._model(X)
        return output

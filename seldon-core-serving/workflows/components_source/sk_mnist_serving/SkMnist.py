import joblib
from sklearn.ensemble import RandomForestClassifier


class SkMnist(object):
    def __init__(self):
        self.clf: RandomForestClassifier  = joblib.load('/models/sk_mnist.pkl') 

    def predict(self, X, feature_names, meta):
        predictions = self.clf.predict_proba(X)
        return predictions

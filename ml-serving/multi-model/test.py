import requests
import argparse
from sklearn import datasets, svm, metrics
from sklearn.datasets import load_svmlight_file
from sklearn.model_selection import train_test_split
import os

# The digits dataset
digits = datasets.load_digits()
n_samples = len(digits.images)
data = digits.images.reshape((n_samples, -1))

X_train, X_test_digits, y_train, y_test_digits = train_test_split(
    data, digits.target, test_size=0.3, shuffle=False)

# NOTE: Workaround to load SVMLight files from the XGBoost example
X_test_agar, y_test_agar = load_svmlight_file('./agaricus.txt.test')
X_test_agar = X_test_agar.toarray()

def predict(model, version):
    if model == 'mnist_sklearn':
        X = X_test_digits
    elif model == 'mushroom_xgboost':
        X = X_test_agar
    else:
        raise ValueError("Model not found!")

    x_0 = X[0:1]
    inference_request = {
        "inputs": [
            {
            "name": "predict",
            "shape": x_0.shape,
            "datatype": "FP32",
            "data": x_0.tolist()
            }
        ]
    }

    endpoint = "http://localhost:9080/v2/models/{}/versions/{}/infer".format(
        model, version
    )
    response = requests.post(endpoint, json=inference_request)
    print(response.json())


if __name__ == "__main__":
    # Argument
    parser = argparse.ArgumentParser('Test model mlserver')
    parser.add_argument('--model', required=True)
    parser.add_argument('--version', required=True)
    args = parser.parse_args()

    # Predict
    predict(args.model, args.version)

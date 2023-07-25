# Original code and extra details can be found in:
# https://xgboost.readthedocs.io/en/latest/get_started.html#python

import os
import xgboost as xgb
import requests

from urllib.parse import urlparse
from sklearn.datasets import load_svmlight_file


TRAIN_DATASET_URL = 'https://raw.githubusercontent.com/dmlc/xgboost/master/demo/data/agaricus.txt.train'
TEST_DATASET_URL = 'https://raw.githubusercontent.com/dmlc/xgboost/master/demo/data/agaricus.txt.test'


def _download_file(url: str) -> str:
    parsed = urlparse(url)
    file_name = os.path.basename(parsed.path)
    file_path = os.path.join(os.getcwd(), file_name)
    
    res = requests.get(url)
    
    with open(file_path, 'wb') as file:
        file.write(res.content)
    
    return file_path

train_dataset_path = _download_file(TRAIN_DATASET_URL)
test_dataset_path = _download_file(TEST_DATASET_URL)

# NOTE: Workaround to load SVMLight files from the XGBoost example
X_train, y_train = load_svmlight_file(train_dataset_path)
X_test_agar, y_test_agar = load_svmlight_file(test_dataset_path)
X_train = X_train.toarray()
X_test_agar = X_test_agar.toarray()

# read in data
dtrain = xgb.DMatrix(data=X_train, label=y_train)

# specify parameters via map
param = {'max_depth':2, 'eta':1, 'objective':'binary:logistic' }
num_round = 2
bst = xgb.train(param, dtrain, num_round)
bst

# Save model
mushroom_xgboost_path = "models/mushroom_xgboost"
os.makedirs(mushroom_xgboost_path, exist_ok=True)

mushroom_xgboost_model_path = os.path.join(mushroom_xgboost_path, "model.json")
bst.save_model(mushroom_xgboost_model_path)

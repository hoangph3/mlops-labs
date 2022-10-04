import pandas as pd
from pathlib import Path
import tensorflow as tf
import pickle
import argparse
import json


def main(args):
    model = tf.keras.models.load_model(args.input_model)
    
    norm_test_X = pd.read_csv(args.input_test_x)
    with open(args.input_test_y, "rb") as file:
        test_Y = pickle.load(file)

    loss, Y1_loss, Y2_loss, Y1_rmse, Y2_rmse = model.evaluate(x=norm_test_X, y=test_Y)
    print("Loss = {}, Y1_loss = {}, Y1_mse = {}, Y2_loss = {}, Y2_mse = {}".format(loss,
                                                                                   Y1_loss,
                                                                                   Y1_rmse,
                                                                                   Y2_loss,
                                                                                   Y2_rmse))

    Path(args.metrics_path).parent.mkdir(parents=True, exist_ok=True)
    metrics = {
        'metrics': [
            {
                'name': 'loss',
                'numberValue': float(loss),
            },
            {
                'name': 'Y1_loss',
                'numberValue': float(Y1_loss),
            },
            {
                'name': 'Y2_loss',
                'numberValue': float(Y2_loss),
            },
            {
                'name': 'Y1_rmse',
                'numberValue': float(Y1_rmse),
            },
            {
                'name': 'Y2_rmse',
                'numberValue': float(Y2_rmse),
            },
        ]
    }
    Path(args.metrics_path).write_text(json.dumps(metrics))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Normalize dataset')
    parser.add_argument('--input_model', type=str, help='model checkpoint')
    parser.add_argument('--input_test_x', type=str, help='test features')
    parser.add_argument('--input_test_y', type=str, help='test labels')
    parser.add_argument('--metrics_path', type=str, help='log metrics')
    args = parser.parse_args()
    main(args)
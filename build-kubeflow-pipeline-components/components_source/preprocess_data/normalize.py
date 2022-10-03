from pathlib import Path
import pandas as pd
import numpy as np
import argparse
import pickle


def format_output(data):
    y1 = data.pop('Y1')
    y1 = np.array(y1)
    y2 = data.pop('Y2')
    y2 = np.array(y2)
    return y1, y2


def norm(x, train_stats):
    return (x - train_stats['mean']) / train_stats['std']


def main(args):
    train = pd.read_csv(args.input_train_csv)
    test = pd.read_csv(args.input_test_csv)

    train_stats = train.describe()
    train_stats.pop('Y1')
    train_stats.pop('Y2')
    train_stats = train_stats.transpose()

    Path(args.output_train_x).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_train_y).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_test_x).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_test_y).parent.mkdir(parents=True, exist_ok=True)

    train_Y = format_output(train)
    with open(args.output_train_y, "wb") as file:
        pickle.dump(train_Y, file)

    test_Y = format_output(test)
    with open(args.output_test_y, "wb") as file:
        pickle.dump(test_Y, file)

    norm_train_X = norm(train, train_stats)
    norm_test_X = norm(test, train_stats)
    norm_train_X.to_csv(args.output_train_x, index=False)
    norm_test_X.to_csv(args.output_test_x, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Normalize dataset')
    parser.add_argument('--input_train_csv', type=str, help='Local path to train CSV dataset')
    parser.add_argument('--input_test_csv', type=str, help='Local path to test CSV dataset')
    
    parser.add_argument('--output_train_x', type=str, help='train features')
    parser.add_argument('--output_train_y', type=str, help='train labels')
    parser.add_argument('--output_test_x', type=str, help='test features')
    parser.add_argument('--output_test_y', type=str, help='test labels')

    args = parser.parse_args()
    main(args)
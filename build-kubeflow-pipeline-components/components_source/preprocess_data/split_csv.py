from sklearn.model_selection import train_test_split
from pathlib import Path
import pandas as pd
import argparse


def main(args):
    df = pd.read_csv(args.input_csv)
    train, test = train_test_split(df, test_size=args.test_size)

    Path(args.train_csv).parent.mkdir(parents=True, exist_ok=True)
    Path(args.test_csv).parent.mkdir(parents=True, exist_ok=True)
    
    train.to_csv(args.train_csv, index=False)
    test.to_csv(args.test_csv, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Split dataset')
    parser.add_argument('--test_size', type=float, help='Test size')
    parser.add_argument('--input_csv', type=str, help='Local path to CSV dataset')
    parser.add_argument('--train_csv', type=str, help='Local path to train CSV dataset')
    parser.add_argument('--test_csv', type=str, help='Local path to test CSV dataset')
    args = parser.parse_args()
    main(args)
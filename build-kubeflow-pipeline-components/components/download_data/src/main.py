from pathlib import Path
import argparse
import pandas as pd


def main(args):
    df = pd.read_excel(args.url)
    df = df.sample(frac=1).reset_index(drop=True)
    df.to_csv(args.output_csv_path, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download CSV dataset')
    parser.add_argument('--url', type=str, help='Link to CSV dataset')
    parser.add_argument('--output_csv_path', type=str, help='Local path to CSV dataset')
    args = parser.parse_args()

    main(args)
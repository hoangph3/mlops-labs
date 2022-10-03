from pathlib import Path
import pandas as pd
import argparse


def main(args):
    df = pd.read_csv(args.url)
    df = df.sample(frac=1).reset_index(drop=True)

    Path(args.output_csv).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output_csv, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download CSV dataset')
    parser.add_argument('--url', type=str, help='URL to CSV dataset')
    parser.add_argument('--output_csv', type=str, help='Local path to CSV dataset')
    args = parser.parse_args()
    main(args)
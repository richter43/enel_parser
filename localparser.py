import argparse


def parse() -> argparse.Namespace:

    parser = argparse.ArgumentParser(description="Parse a ENI website for extracting data")
    parser.add_argument("--filename", type=str, required=True, help="Name of the file that contains the URLs")
    parser.add_argument("--output_file", type=str, default="output.csv", help="Name of the output file")

    args = parser.parse_args()

    return args

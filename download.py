import argparse
from niklibrary.web.Download import Download


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='OTA payload dumper')
    parser.add_argument('--download', default="", help='folder to read from')
    args = parser.parse_args()
    Download.url(args.download)
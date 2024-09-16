import argparse
import os
import re

from NikGapps.helper.FileOp import FileOp
from dotenv import load_dotenv

parser = argparse.ArgumentParser(description='OTA payload dumper')
parser.add_argument('--folder', default="", help='folder to read from')
args = parser.parse_args()

file_name = str(args.folder)
pattern = r'([a-zA-Z]+)-ota-\w+\.(\d{6})'
match = re.search(pattern, file_name)
if match:
    device_name = match.group(1)
    date = match.group(2)
    test = match.groups()
    file_name = f"{device_name}_{date}"
load_dotenv()
print(f"File name: {file_name}")
if FileOp.dir_exists(file_name):
    print(f"Directory exists: {file_name}")
    for root, dirs, files in os.walk(file_name):
        for file in files:
            print(f"File: {file}")
else:
    print(f"Directory does not exist: {file_name}")


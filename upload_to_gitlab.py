import argparse
import re

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


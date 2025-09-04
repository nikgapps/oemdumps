import argparse

from niklibrary.oem.OemOp import OemOp

device_name = "caiman"
google_devices = {
    "panther": "Pixel 7",
    "cheetah": "Pixel 7 Pro",
    "lynx": "Pixel 7a",
    "shiba": "Pixel 8",
    "husky": "Pixel 8 Pro",
    "akita": "Pixel 8a",
    "felix": "Pixel Fold",
    "tangorpro": "Pixel Tablet",
    "tokay": "Pixel 9",
    "caiman": "Pixel 9 Pro",
    "komodo": "Pixel 9 Pro XL",
    "comet": "Pixel 9 Pro Fold",
    "mustang": "Pixel 10 Pro XL"
}

parser = argparse.ArgumentParser(description='OTA payload dumper')
parser.add_argument('--download', default="caiman", help='folder to read from')
args = parser.parse_args()
url = args.download

# Convert the dictionary to lower case for case-insensitive comparison
google_devices_lower = {k.lower(): v.lower() for k, v in google_devices.items()}

if url.lower() in google_devices_lower.keys():
    url = OemOp.get_latest_ota_url(url.lower())
elif url.lower() in google_devices_lower.values():
    device_name = list(google_devices_lower.keys())[list(google_devices_lower.values()).index(url.lower())]
    url = OemOp.get_latest_ota_url(device_name)
else:
    url = args.download

print(url)

import argparse
from niklibrary.oem.OemOp import OemOp
from niklibrary.web.Download import Download

if __name__ == "__main__":
    google_devices = {
        "sailfish": "Pixel",
        "marlin": "Pixel XL",
        "walleye": "Pixel 2",
        "taimen": "Pixel 2 XL",
        "blueline": "Pixel 3",
        "crosshatch": "Pixel 3 XL",
        "sargo": "Pixel 3a",
        "bonito": "Pixel 3a XL",
        "flame": "Pixel 4",
        "coral": "Pixel 4 XL",
        "sunfish": "Pixel 4a",
        "bramble": "Pixel 4a (5G)",
        "redfin": "Pixel 5",
        "barbet": "Pixel 5a",
        "oriole": "Pixel 6",
        "raven": "Pixel 6 Pro",
        "bluejay": "Pixel 6a",
        "panther": "Pixel 7",
        "cheetah": "Pixel 7 Pro",
        "lynx": "Pixel 7a",
        "shiba": "Pixel 8",
        "husky": "Pixel 8 Pro",
        "akita": "Pixel 8a",
        "felix": "Pixel Fold",
        "tangorpro": "Pixel Tablet",
        "bluefin": "Pixel Buds",
        "tokay": "Pixel 9",
        "caiman": "Pixel 9 Pro",
        "komodo": "Pixel 9 Pro XL",
        "comet": "Pixel 9 Pro Fold"
    }

    parser = argparse.ArgumentParser(description='OTA payload dumper')
    parser.add_argument('--download', default="", help='folder to read from')
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

    Download.url(url)
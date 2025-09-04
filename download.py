import argparse
from niklibrary.oem.OemOp import OemOp
from niklibrary.web.Download import Download

if __name__ == "__main__":
    google_devices = OemOp.get_google_devices()

    if google_devices is None:
        google_devices = {
            "caiman": "Pixel 9 Pro",
            "mustang": "Pixel 10 Pro XL"
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
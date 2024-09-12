from OTAUpdater import OTAUpdater

device_name = "husky"
o = OTAUpdater()
categorized_url = o.get_latest_ota_url(device_name)
print(categorized_url)

# https://dl.google.com/dl/android/aosp/caiman-ota-ad1a.240905.004-36913b8a.zip

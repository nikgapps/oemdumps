from niklibrary.oem.Google import Google


device_name = "caiman"
g = Google(device_name)
print(g.get_latest_ota_url())

# https://dl.google.com/dl/android/aosp/caiman-ota-ad1a.240905.004-36913b8a.zip

from OTAUpdater import OTAUpdater

device_name = "husky"
o = OTAUpdater()
categorized_url = o.get_latest_ota_url(device_name)
filepath = o.download_file(categorized_url)
print(categorized_url)

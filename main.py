import zipfile

from OTAUpdater import OTAUpdater

device_name = "husky"
extract_folder = "extracted"
o = OTAUpdater()
categorized_url = o.get_latest_ota_url(device_name)
base_name = categorized_url.split('/')[-1]
filepath = o.download_file(categorized_url)
with zipfile.ZipFile(filepath, 'r') as zip_ref:
    for file_info in zip_ref.infolist():
        if file_info.filename.endswith('payload.bin'):
            output_dir = "/payload_dumper"
            zip_ref.extract(file_info, output_dir)
            break
print(categorized_url)

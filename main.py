import os
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
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            full_path = os.path.join(parent_dir, "payload_dumper")
            zip_ref.extract(file_info, full_path)
            break
print(categorized_url)

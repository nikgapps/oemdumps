import zipfile

from niklibrary.oem.OemOp import OemOp
from niklibrary.web.Download import Download

device_name = "husky"
extract_folder = "extracted"
categorized_url = OemOp.get_latest_ota_url(device_name)
base_name = categorized_url.split('/')[-1]
filepath = Download.url(categorized_url)
with zipfile.ZipFile(filepath, 'r') as zip_ref:
    for file_info in zip_ref.infolist():
        if file_info.filename.endswith('payload.bin'):
            zip_ref.extract(file_info, extract_folder)
            break
print(categorized_url)

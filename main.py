import zipfile
from niklibrary.oem.Google import Google
from niklibrary.web.Download import Download

device_name = "husky"
extract_folder = "extracted"
g = Google(device_name)
categorized_url = g.get_latest_ota_url()
base_name = categorized_url.split('/')[-1]
filepath = Download.url(categorized_url)
with zipfile.ZipFile(filepath, 'r') as zip_ref:
    for file_info in zip_ref.infolist():
        if file_info.filename.endswith('payload.bin'):
            zip_ref.extract(file_info, extract_folder)
            break
print(categorized_url)

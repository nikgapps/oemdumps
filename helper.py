import re


def get_repo_name(file_name):
    pattern = r'([a-zA-Z_]+)-ota-\w+\.(\d{6})'
    match = re.search(pattern, file_name)
    if match:
        device_name = match.group(1)
        date = match.group(2)
        return device_name, date
    return file_name, None


# def extract_build_info(file_name):
#     rom_patterns = {
#         # "Project_Infinity-X": r"^(Project_Infinity-X)-(\d+\.\d+)-(vayu)-(\d{8})-\d{4}-(VANILLA|GAPPS)-OFFICIAL$",
#         # Add more patterns here if you have other ROM names
#         # cheetah_beta-ota-ap41.240823.009-971ac562.zip
#         "cheetah_beta": r"^(cheetah_beta)-ota-\w+\.(\d{6})"
#     }
#
#     for rom_name, pattern in rom_patterns.items():
#         match = re.search(pattern, file_name)
#         if match:
#             return {
#                 "rom_name": rom_name,
#                 "version": match.group(2),
#                 # "device": match.group(3),
#                 # "build_date": match.group(4),
#                 # "type": match.group(5)
#             }
#     return None
#
# # Example usage
# filenames = [
#     # "Project_Infinity-X-1.5-vayu-20240910-0918-VANILLA-OFFICIAL",
#     # "Project_Infinity-X-1.5-vayu-20240910-1031-GAPPS-OFFICIAL",
#     "cheetah_beta-ota-ap41.240823.009-971ac562"
# ]
#
# for filename in filenames:
#     build_info = extract_build_info(filename)
#     if build_info:
#         print(f"Filename: {filename}")
#         print(f"  ROM Name: {build_info['rom_name']}")
#         print(f"  Version: {build_info['version']}")
#         # print(f"  Device: {build_info['device']}")
#         # print(f"  Build Date: {build_info['build_date']}")
#         # print(f"  Type: {build_info['type']}")
#     else:
#         print(f"No match found for filename: {filename}")
#
# print(get_repo_name("caiman-ota-ad1a.240905.004-36913b8a"))

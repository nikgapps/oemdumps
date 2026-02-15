import os
from datetime import datetime, timezone

from niklibrary.helper.F import F


class FileOp(F):

    @staticmethod
    def get_repo_name(source_directory):
        android_version = None
        build_date = None
        device_name = None

        android_version_keys = {
            "ro.product.build.version.release",
            "ro.build.version.release",
            "ro.system.build.version.release",
        }

        build_date_keys = {
            "ro.product.build.date.utc",
            "ro.system_ext.build.date.utc",
            "ro.system.build.date.utc",
        }

        device_name_keys = {
            "ro.product.product.device",
            "ro.product.system_ext.device",
            "ro.product.system.device",
        }

        target_folders = {"product/etc", "system_ext/etc", "system"}

        for root, _, files in os.walk(source_directory):
            normalized_root = root.replace("\\", "/")

            if not any(folder in normalized_root for folder in target_folders):
                continue

            for file in files:
                if not file.endswith("build.prop"):
                    continue

                path = os.path.join(root, file)

                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if "=" not in line:
                            continue

                        key, value = line.strip().split("=", 1)
                        # android version
                        if key in android_version_keys:
                            android_version = value
                        # build date
                        elif key in build_date_keys:
                            build_date = datetime.fromtimestamp(
                                float(value), tz=timezone.utc
                            ).strftime("%Y%m%d")
                        # device name
                        elif key in device_name_keys:
                            device_name = value

                        if android_version and build_date and device_name:
                            return android_version, build_date, device_name

        return android_version, build_date, device_name

import os
import re
from datetime import datetime, timezone

from niklibrary.helper.F import F


class FileOp(F):

    @staticmethod
    def get_repo_info(source_directory):
        android_version = None
        build_date = None
        device_name = None
        brand = None
        fingerprint = None

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

        brand_keys = {
            "ro.product.product.brand",
            "ro.product.system_ext.brand",
            "ro.product.system.brand"
        }

        fingerprint_keys = {
            "ro.product.build.fingerprint",
            "ro.system_ext.build.fingerprint",
            "ro.system.build.fingerprint"
        }

        target_folders = {"product/etc", "system_ext/etc", "system"}
        candidates = []

        for root, _, files in os.walk(source_directory):
            normalized_root = root.replace("\\", "/")

            if not any(folder in normalized_root for folder in target_folders):
                continue

            for file in files:
                if not file.endswith("build.prop"):
                    continue
                candidates.append((normalized_root, os.path.join(root, file)))

        for folder in target_folders:
            for normalized_root, path in candidates:
                if not normalized_root.endswith(folder):
                    continue

                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    print(f"Reading {path} for repo info...")
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
                        # brand
                        elif key in brand_keys:
                            brand = value
                        # fingerprint
                        elif key in fingerprint_keys:
                            fingerprint = value
                        if android_version and build_date and device_name and brand and fingerprint:
                            print(
                                f"android_version={android_version}, build_date={build_date}, device_name={device_name}, brand={brand}, fingerprint={fingerprint}")
                            return android_version, build_date, device_name, brand, fingerprint

        return android_version, build_date, device_name, brand, fingerprint

    @staticmethod
    def detect_partitions(source_directory, skip_partitions=None):
        if skip_partitions is None:
            skip_partitions = set()

        candidate_partitions = {"system", "product", "system_ext"}
        detected = {}

        for root, dirs, _ in os.walk(source_directory):
            base = os.path.basename(root)

            if base in candidate_partitions and base not in skip_partitions:
                # Check if it contains Android typical structure
                subdirs = set(dirs)
                if {"app", "priv-app", "framework"} & subdirs:
                    relative = os.path.relpath(root, source_directory).replace("\\", "/")
                    if base not in detected:
                        detected[base] = relative

        return detected

    @staticmethod
    def get_build_date_from_fingerprint(fingerprint):
        match = re.search(r'\.(\d{6})\.', fingerprint)
        return match.group(1) if match else None

    @staticmethod
    def detect_variant_from_path(path: str, variant_map: dict, brand: str) -> str | None:
        path_lower = path.lower()

        for variant, keywords in variant_map.items():
            if any(keyword in path_lower for keyword in keywords):
                return variant
        if brand != "google":
            gms_markers = {
                "Phonesky.apk"
            }

            for root, _, files in os.walk(path):
                for file in files:
                    if file in gms_markers:
                        return "gapps"

        return None
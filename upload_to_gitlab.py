import argparse
import os
from pathlib import Path

from niklibrary.git.GitOp import GitOp
from niklibrary.git.GitlabManager import GitLabManager
from niklibrary.helper.F import F
from dotenv import load_dotenv
from niklibrary.build.Overlay import Overlay
from niklibrary.helper.P import P
from niklibrary.helper.SystemStat import SystemStat
from niklibrary.json.Json import Json
from niklibrary.oem.OemOp import OemOp

from helper.FileOp import FileOp

SystemStat.show_stats()
parser = argparse.ArgumentParser(description='OTA payload dumper')
parser.add_argument('--folder', default="", help='folder to read from')
# parser.add_argument('--skip', nargs='*', default=['system', 'product'])
parser.add_argument('--skip', nargs='*', default=[])
args = parser.parse_args()

source_directory = str(args.folder)
skip_partitions=set(args.skip)

print(f"Source Directory: {source_directory}")
android_version, build_date, device_name, brand, fingerprint = None, None, None, None, None
if FileOp.dir_exists(source_directory):
    android_version, build_date, device_name, brand, fingerprint = FileOp.get_repo_info(source_directory)
    if brand == "google":
        build_date = FileOp.get_build_date_from_fingerprint(fingerprint)
if not android_version or not build_date or not device_name:
    exit("Android version, Build Date and Device name are required")

variant_keywords = {
    "gapps": ["gapps", "gms", "banshee"],
    "vanilla": ["vanilla", "aosp"],
}

variant = FileOp.detect_variant_from_path(source_directory, variant_keywords, brand)
variant = "vanilla" if brand != "google" and not variant else variant

repo_name = f"{android_version}_{device_name}" + (f"_{variant}" if variant else "") + (f"_{build_date}" if build_date else "")

print(f"Repo name: {repo_name}")
load_dotenv()

if F.dir_exists(source_directory):
    print(f"Directory exists: {source_directory}")
    gitlab_token = os.getenv("GITLAB_TOKEN")
    working_dir = str(Path(source_directory).parent)
    print(f"Working directory: {working_dir}")
    partitions = FileOp.detect_partitions(source_directory)
    exclude_folders = [f"system{os.sep}system", f"oat{os.sep}"]
    include_folders = ["app", "priv-app", "etc", "framework", "lib64", "overlay", "tts", "usr", "lib"]
    must_include_files = ["build.prop", ".apk"]
    must_exclude_files = [".prop", ".vdex", ".odex"]
    output_folder = "output"
    gitlab_manager = GitLabManager(private_token=gitlab_token)
    project = gitlab_manager.get_project(repo_name)
    if not project:
        gitattributes = """*.apk filter=lfs diff=lfs merge=lfs -text
        *.so filter=lfs diff=lfs merge=lfs -text"""
        project = gitlab_manager.create_repository(repo_name, provide_owner_access=True)
        commit = gitlab_manager.create_and_commit_file(project_id=project.id, file_path=".gitattributes",
                                                       content=gitattributes)
    else:
        print(f"Project already exists: {project.name}")
    repo_dir = working_dir + os.sep + repo_name
    repo = GitOp.setup_repo(repo_dir=repo_dir,
                                    repo_url=project.ssh_url_to_repo)
    for partition in partitions:
        if partition in skip_partitions:
            print(f"Skipping {partition} partition as it is in skip list")
            continue
        source_dir = f"{source_directory}{os.sep}{partitions[partition]}"
        print(f"Source: {source_dir}")
        if not os.path.exists(source_dir):
            print(f"{source_dir} does not exist")
            continue

        destination_dir = f"{repo.working_tree_dir}/{partition}"

        print(f"Destination: {destination_dir}")

        for root, _, files in os.walk(source_dir):
            for file in files:
                skip_further_check = False
                file_path = os.path.join(root, file)
                if any(file.endswith(extension) for extension in must_include_files):
                    P.green(f"Copying {file_path} as it is in must include files")
                    skip_further_check = True
                if not skip_further_check:
                    if any(folder in file_path for folder in exclude_folders):
                        P.yellow(f"Skipping {file_path} as it is in exclude folder")
                        continue
                    if any(file.endswith(extension) for extension in must_exclude_files):
                        P.blue(f"Skipping {file_path} as it is in must exclude files")
                        continue
                    if not any(f"{folder}{os.sep}" in file_path for folder in include_folders):
                        P.magenta(f"Skipping {file_path} as it is not in include folders")
                        continue
                relative_path = os.path.relpath(file_path, source_dir)
                destination_path = os.path.join(destination_dir, relative_path)
                if not F.file_exists(file_path):
                    P.red(f"File does not exist: {file_path}")
                    continue
                file_size = os.path.getsize(file_path) / (1024 * 1024)
                F.copy_file(file_path, destination_path)
                P.green(f"Copied {file_path} "
                        f"\n  to {destination_path}"
                        f"\nSize: {file_size:.2f} MB")
                if destination_path.lower().__contains__(os.sep + "overlay"):
                    o = Overlay(destination_path)
                    if not o.extract_overlay():
                        print("Overlay extraction of " + destination_path + " failed")

        filename = device_name + ".json"
        filename_dict = OemOp.get_google_oem_dump_dict_async(repo.working_tree_dir)
        print(f"Writing {filename} to {repo.working_tree_dir}{os.sep}{filename}")
        Json.write_dict_to_file(filename_dict, f"{repo.working_tree_dir}{os.sep}{filename}")

        if repo.due_changes():
            OemOp.write_all_files(repo.working_tree_dir)
            repo.git_push(f"Pushing {partition} files", push_untracked_files=True, debug=True, pull_first=True)
        else:
            print("No changes to push")

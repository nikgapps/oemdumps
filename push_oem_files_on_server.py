import os

from NikGapps.helper.FileOp import FileOp
from NikGapps.helper.P import P
from NikGapps.helper.git.GitOperations import GitOperations
from NikGapps.helper.git.GitlabManager import GitLabManager
from dotenv import load_dotenv


load_dotenv()
gitlab_token = os.getenv("GITLAB_TOKEN")
working_dir = os.getcwd()
print(f"Working directory: {working_dir}")
partitions = ["system", "product", "system_ext"]
exclude_folders = [f"system{os.sep}system", f"oat{os.sep}"]
include_folders = ["app", "priv-app", "etc", "framework", "lib64", "overlay", "tts", "usr", "lib"]
must_include_files = [".prop", ".apk"]
output_folder = "output"
android_version = "14"
oem = "husky"
repo_name = f"{android_version}_{oem}"
repo_dir = working_dir + os.sep + output_folder + os.sep + repo_name
gitlab_manager = GitLabManager(private_token=gitlab_token)
project = gitlab_manager.get_project(repo_name)
if project:
    message = """*.apk filter=lfs diff=lfs merge=lfs -text
*.so filter=lfs diff=lfs merge=lfs -text"""
    gitlab_manager.reset_repository(project.path, gitattributes=message)
else:
    project = gitlab_manager.create_repository(repo_name)
repo = GitOperations.setup_repo(repo_dir=repo_dir,
                                repo_url=project.ssh_url_to_repo)
for partition in partitions:
    source_dir = f"{working_dir}{os.sep}{output_folder}{os.sep}{partition}"
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
                skip_further_check = True
            if not skip_further_check:
                if not any(folder in file_path for folder in exclude_folders):
                    continue
                if not any(f"{folder}{os.sep}" in file_path for folder in include_folders):
                    continue
            relative_path = os.path.relpath(file_path, source_dir)
            destination_path = os.path.join(destination_dir, relative_path)
            P.green(f"Copying {file_path} to {destination_path}")
            FileOp.copy_file(file_path, destination_path)

if repo.due_changes():
    repo.git_push("Pushing OEM files", push_untracked_files=True)
else:
    print("No changes to push")

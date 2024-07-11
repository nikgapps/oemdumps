import os
from NikGapps.helper.git.GitOperations import GitOperations
from NikGapps.helper.git.GitlabManager import GitLabManager

partitions = ["system", "product", "system_ext"]
output_folder = "output"
android_version = "14"
oem = "husky"
repo_name = f"{android_version}_{oem}"
gitlab_manager = GitLabManager(private_token='glpat-2yU9tSz99acWf_xPGbNq')
project = gitlab_manager.get_project(repo_name)
if project:
    gitlab_manager.reset_repository(project.path)
else:
    project = gitlab_manager.create_repository(repo_name)
repo = GitOperations.setup_repo(repo_dir=repo_name, repo_url=project.ssh_url_to_repo)

for partition in partitions:
    source_dir = f"{output_folder}{os.sep}{partition}"
    if not os.path.exists(source_dir):
        print(f"{source_dir} does not exist")
        continue
    repo_dir = f"{repo.working_tree_dir}/{partition}"
    for root, _, files in os.walk(source_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if partition == "system":
                if f"system{os.sep}system" not in file_path:
                    continue
            if f"app{os.sep}" not in file_path:
                continue
            relative_path = os.path.relpath(file_path, source_dir)
            destination_path = os.path.join(repo_dir, relative_path)
            print(f"Copying {file_path} to {destination_path}")

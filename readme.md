## When we want to validate if the docker is running

```bash
wsl --list --verbose
```

## When we want to build the image locally

```bash
docker build -t afe .
```

## When we want to mount the directory to run it on local

this helps when we want to avoid downloading files for rerun purpose, we can keep the zip file at the mounted directory and let the program pick it up from there instead of downloading it again

```bash
docker run --rm -it -e GITLAB_TOKEN="..." -e URL="https://mirror.codebucket.de/yaap/vayu/vanilla/YAAP-16-Vanilla-vayu-20260126.zip" -v F:\oem_files:/mnt/host_files afe "/usr/src/workdir/run.sh"
```

## When we want to run it similar to how we run on github server (workflows)

```bash
docker run --rm -it -e GITLAB_TOKEN="..." -e URL="https://dl.google.com/dl/android/aosp/mustang-ota-bp4a.260205.001.c1-9a99581b.zip" afe "/usr/src/workdir/run.sh"
```

## Few other examples
```bash
docker run --rm -it -e GITLAB_TOKEN="..." -e URL="https://dl.google.com/dl/android/aosp/mustang-ota-bp4a.260205.001.c1-9a99581b.zip" -v F:\oem_files:/mnt/host_files afe /bin/sh

docker run --rm -it -e GITLAB_TOKEN="..." -e URL="https://dl.google.com/dl/android/aosp/mustang-ota-bp4a.260205.001.c1-9a99581b.zip" -v F:\oem_files:/mnt/host_files afe "cd /mnt/host_files && /usr/src/workdir/run.sh"

docker run --rm -it -e GITLAB_TOKEN="..." -e URL="https://dl.google.com/dl/android/aosp/mustang-ota-bp4a.260205.001.c1-9a99581b.zip" -v F:\oem_files:/mnt/host_files afe "cd /mnt/host_files && /usr/src/workdir/run.sh"

docker run --rm -it -e GITLAB_TOKEN="..." -e URL="https://mirror.codebucket.de/yaap/vayu/YAAP-16-Banshee-vayu-20260126.zip" -v F:\oem_files:/mnt/host_files afe "/usr/src/workdir/run.sh"

docker run --rm -it -e GITLAB_TOKEN="..." -e URL="https://mirror.codebucket.de/yaap/vayu/vanilla/YAAP-16-Vanilla-vayu-20260126.zip" -v F:\oem_files:/mnt/host_files afe "/usr/src/workdir/run.sh"
```

## When we want to execute the run.sh manually
```bash
docker run --rm -it afe bash
ls -l /usr/src/workdir/run.sh
```

## When we want to shrink the size taken by vhdx file on the disk
```bash
diskpart

select vdisk file="F:\Docker\DockerDesktopWSL\disk\docker_data.vhdx"
attach vdisk readonly
compact vdisk
detach vdisk
exit
```

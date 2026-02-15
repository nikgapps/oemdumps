# Docker Local Development Guide (afe Project)

This guide contains all essential Docker commands for building, running,
debugging, and cleaning up your local environment.

------------------------------------------------------------------------

## 1️⃣ Building the Image

### Normal Build (Recommended)

Uses cache for faster rebuilds. docker build -t afe .

### Clean Rebuild (No Cache)

For debugging or dependency changes. docker build --no-cache -t afe .

### Remove Image Before Rebuild

Prevents multiple versions stacking. docker rmi afe docker build -t afe
.

------------------------------------------------------------------------

## 2️⃣ Running the Container

### Run (Same as GitHub Workflow)

docker run --rm -it -e GITLAB_TOKEN="your_token" -e URL="your_url" afe
"/usr/src/workdir/run.sh"

### Run With Mounted Folder (Persistent Downloads)

Downloads and extracted files saved to F:`\oem`{=tex}\_files. docker run
--rm -it -e GITLAB_TOKEN="your_token" -e URL="your_url" -v
F:`\oem`{=tex}\_files:/mnt/host_files afe "/usr/src/workdir/run.sh"

------------------------------------------------------------------------

## 3️⃣ Debugging & Interactive Mode

### Open Shell Inside Container

docker run --rm -it afe bash

### Run Without Auto-Remove

Allows inspection after execution. docker run -it --name afe-test afe
bash

### Attach to Running Container

docker exec -it afe-test bash

------------------------------------------------------------------------

## 4️⃣ Inspect Docker State

### List Images

docker images

### List Containers

docker ps -a

### Check Disk Usage

docker system df

------------------------------------------------------------------------

## 5️⃣ Cleanup Commands

### Remove Stopped Containers

docker container prune

### Remove Build Cache

docker builder prune

### Remove Unused Images

docker image prune

### Full Cleanup (Aggressive)

Removes all unused images, containers, networks. docker system prune -a

### Remove Specific Image

docker rmi afe

------------------------------------------------------------------------

## 6️⃣ WSL2 Disk Shrinking (If Using WSL Backend)

### Shutdown WSL

wsl --shutdown

### Compact VHD (Admin PowerShell)

diskpart select vdisk
file="F:`\Docker`{=tex}`\DockerDesktopWSL`{=tex}`\docker`{=tex}\_data.vhdx"
attach vdisk readonly compact vdisk detach vdisk exit

------------------------------------------------------------------------

## 7️⃣ Best Practices

-   Use --rm for temporary runs.
-   Avoid creating multiple tags unless needed.
-   Periodically run docker builder prune.
-   Use --no-cache only when necessary.
-   Mount folders only when persistence is required.
-   Rebuild cleanly after major script changes.

------------------------------------------------------------------------

End of guide.

# Use an official Ubuntu base image
FROM ubuntu:24.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    build-essential \
    libguestfs-tools \
    e2fsprogs \
    android-sdk-libsparse-utils \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    python3-pip \
    brotli \
    git \
    git-lfs \
    unace \
    unrar \
    zip \
    unzip \
    p7zip-full \
    p7zip-rar \
    sharutils \
    rar \
    uudeview \
    mpack \
    arj \
    cabextract \
    device-tree-compiler \
    liblzma-dev \
    liblz4-tool \
    axel \
    gawk \
    aria2 \
    detox \
    cpio \
    rename \
    wget \
    curl \
    openjdk-17-jdk \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Clone necessary repositories
RUN git clone --recurse-submodules https://github.com/AndroidDumps/Firmware_extractor.git /Firmware_extractor \
 && git clone --recurse-submodules https://github.com/carlitros900/mkbootimg_tools.git /mkbootimg_tools \
 && git clone --recurse-submodules https://github.com/marin-m/vmlinux-to-elf.git /vmlinux-to-elf \
 && git clone https://github.com/vm03/payload_dumper.git /payload_dumper \
 && git clone https://github.com/xpirt/sdat2img.git /sdat2img

# Install Python packages
RUN python3.12 -m venv /venv && \
    . /venv/bin/activate && \
    pip install --no-cache-dir --upgrade pip

# Set work directory
WORKDIR /usr/src/workdir

# Copy the rest of the application code into the container
COPY . .

# Ensure all .sh scripts have execute permissions
RUN find . -name "*.sh" -exec chmod +x {} +

# Set the entrypoint
ENTRYPOINT ["bash", "-c"]

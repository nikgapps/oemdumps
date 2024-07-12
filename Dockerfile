# Use an official Ubuntu base image with Python 3.12
FROM ubuntu:23.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies including Python 3.12 and pip
RUN apt-get update && apt-get install -y \
    git \
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
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    python3-pip \
    brotli \
    liblz4-tool \
    axel \
    gawk \
    aria2 \
    detox \
    cpio \
    rename \
    liblz4-dev \
    wget \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /usr/src/workdir

# Create a virtual environment and install Python packages
RUN python3.12 -m venv venv
ENV PATH="/usr/src/workdir/venv/bin:$PATH"
RUN pip install --upgrade pip \
 && pip install aospdtgen backports.lzma extract-dtb protobuf==3.20.1 pycryptodome docopt zstandard

# Clone necessary repositories with submodules
RUN git clone --recurse-submodules https://github.com/AndroidDumps/Firmware_extractor.git /Firmware_extractor \
 && git clone --recurse-submodules https://github.com/carlitros900/mkbootimg_tools.git /mkbootimg_tools \
 && git clone --recurse-submodules https://github.com/marin-m/vmlinux-to-elf.git /vmlinux-to-elf \
 && git clone https://github.com/vm03/payload_dumper.git /payload_dumper

# Install dependencies for payload_dumper
WORKDIR /payload_dumper
RUN /usr/src/workdir/venv/bin/pip install -r requirements.txt

# Set work directory
WORKDIR /usr/src/workdir

# Copy the script into the container
COPY extract_ota_update.sh /usr/src/workdir/extract_ota_update.sh
RUN chmod +x /usr/src/workdir/extract_ota_update.sh

# Set the entrypoint
ENTRYPOINT ["bash", "/usr/src/workdir/extract_ota_update.sh"]

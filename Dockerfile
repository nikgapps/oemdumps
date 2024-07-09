# Use an official Ubuntu base image
FROM ubuntu:20.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Update and install dependencies
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
    python3-venv \
 && rm -rf /var/lib/apt/lists/*

# Clone necessary repositories with submodules
RUN git clone --recurse-submodules https://github.com/AndroidDumps/Firmware_extractor.git /Firmware_extractor \
 && git clone --recurse-submodules https://github.com/carlitros900/mkbootimg_tools.git /mkbootimg_tools \
 && git clone --recurse-submodules https://github.com/marin-m/vmlinux-to-elf.git /vmlinux-to-elf

# Set up the virtual environment and install Python dependencies
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN pip install --upgrade pip \
 && pip install aospdtgen backports.lzma extract-dtb protobuf pycryptodome docopt zstandard


# Set work directory
WORKDIR /usr/src/workdir

# Create a virtual environment and install Python packages
RUN python3 -m venv venv
ENV PATH="/usr/src/workdir/venv/bin:$PATH"
RUN pip install --upgrade pip

# Copy the script into the container
COPY extract_ota_update.sh /usr/src/workdir/extract_ota_update.sh
RUN chmod +x /usr/src/workdir/extract_ota_update.sh

# Set the entrypoint
ENTRYPOINT ["bash", "/usr/src/workdir/extract_ota_update.sh"]

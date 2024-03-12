#!/usr/bin/env bash

echo "Hello, World!"


# Determine which command to use for privilege escalation
if command -v sudo > /dev/null 2>&1; then
    sudo_cmd="sudo"
elif command -v doas > /dev/null 2>&1; then
    sudo_cmd="doas"
else
    echo "Neither sudo nor doas found. Please install one of them."
    # exit 1
fi

# download or copy from local?
if echo "$link" | grep -e '^\(https\?\|ftp\)://.*$' > /dev/null; then
    # 1DRV URL DIRECT LINK IMPLEMENTATION
    if echo "$1" | grep -e '1drv.ms' > /dev/null; then
        URL=`curl -I "$1" -s | grep location | sed -e "s/redir/download/g" | sed -e "s/location: //g"`
    else
        URL=$1
    fi
    { type -p aria2c > /dev/null 2>&1 && printf "Downloading File...\n" && aria2c -x16 -j"$(nproc)" "${URL}"; } || { printf "Downloading File...\n" && wget -q --content-disposition --show-progress --progress=bar:force "${URL}" || exit 1; }
    if [[ ! -f "$(echo ${URL##*/} | inline-detox)" ]]; then
        URL=$(wget --server-response --spider "${URL}" 2>&1 | awk -F"filename=" '{print $2}')
    fi
    detox "${URL##*/}"
else
    URL=$(printf "%s\n" "$1")
    [[ -e "$URL" ]] || { echo "Invalid Input" && exit 1; }
fi

ORG=AndroidDumps #your GitHub org name
FILE=$(echo ${URL##*/} | inline-detox)
EXTENSION=$(echo ${URL##*.} | inline-detox)
UNZIP_DIR=${FILE/.$EXTENSION/}

bash "/Firmware_extractor/extractor.sh" "${FILE}" "${UNZIP_DIR}"

ls -R
#!/bin/bash

set -e

source /venv/bin/activate
source functions.sh

fetch_env_vars
setup_ssh "$SSH_PRIVATE_KEY"
setup_git

primary_repo="oemdumps"
git clone git@github.com:nikgapps/$primary_repo.git
cd $primary_repo
pip3 install -r requirements.txt
FILE=$(get_base_name $URL)
echo "File name is $FILE"
EXTENSION=$(echo ${FILE##*.} | inline-detox)
UNZIP_DIR=${FILE/.$EXTENSION/}
if [ -f "/mnt/host_files/$FILE" ]; then
    echo "ZIP file found from mounted partition!"
    UNZIP_DIR="/mnt/host_files/$UNZIP_DIR"
    FILE="/mnt/host_files/$FILE"
else
    echo "ZIP file not found from mounted partition!"
    echo "Downloading $URL..."
    python3 download.py --download $URL
fi

rm -rf "$UNZIP_DIR"
mkdir -p "$UNZIP_DIR"

partition_list="system product system_ext"
# partition_list="system_ext"

unzip -l "$FILE"

if unzip -l "$FILE" | grep -q "META-INF/com/android/metadata"; then
    echo "Extracting metadata from the zip file..."
    unzip -j "$FILE" "META-INF/com/android/metadata" -d "$UNZIP_DIR"
    cat "$UNZIP_DIR/metadata"
    ANDROID_VERSION=$(grep '^post-build=' "$UNZIP_DIR/metadata" | cut -d ':' -f 2 | cut -d '/' -f 1)
    echo "Android Version: $ANDROID_VERSION"
    echo "$ANDROID_VERSION" > "$UNZIP_DIR/android_version.txt"
    echo "Android version information saved to $UNZIP_DIR/android_version.txt"
fi

if unzip -l "$FILE" | grep -q "payload.bin"; then
    echo "Extracting payload.bin from the zip file..."
    unzip -j "$FILE" "payload.bin" -d "$UNZIP_DIR"
    echo "Extracting payload.bin..."
    for p in $partition_list; do
        echo "Extracting $p.img from payload.bin..."
        python3 /payload_dumper/payload_dumper.py "$UNZIP_DIR/payload.bin" --images "$p" --out "$UNZIP_DIR"
    done
    rm -rf "$UNZIP_DIR/payload.bin"
else
    for p in $partition_list; do
        if unzip -l "$FILE" | grep -q "$p.new.dat.br"; then
            IMG_FILES="$p.new.dat.br $p.transfer.list"
            for img_file in $IMG_FILES; do
                echo "Extracting $img_file from the zip file..."
                unzip -j "$FILE" "$img_file" -d "$UNZIP_DIR"
            done
        else
            echo "$p.new.dat.br not found in the zip file."
        fi
    done
fi

echo "Extraction complete. Files extracted to $UNZIP_DIR"
echo "-----------------------------------------------"
cd $UNZIP_DIR
ls
echo "-----------------------------------------------"
for p in $partition_list; do
    if [ -f "$p.new.dat.br" ]; then
        extract_dat_br $p
    elif [ -f "$p.img" ]; then
        echo "$p.img found."
        extract_img_7z "$p"
    else
        echo "$p.new.dat.br or $p.img not found."
    fi
done
echo "ANDROID_VERSION before: $ANDROID_VERSION"
for p in $partition_list; do
    ANDROID_VERSION=""
    if [ -f "android_version.txt" ]; then
        ANDROID_VERSION=$(cat android_version.txt)
        if [ -n "$ANDROID_VERSION" ]; then
            break
        fi
    else
        echo "Fetching Android version from $p partition..."
        ANDROID_VERSION=$(fetch_android_version $p)
        if [ -n "$ANDROID_VERSION" ]; then
            break
        fi
    fi
done
ls
echo "-----------------------------------------------"
cd ..
ls
echo "-----------------------------------------------"
echo "ANDROID_VERSION: $ANDROID_VERSION"
echo "-----------------------------------------------"
#cd /usr/src/workdir/$primary_repo
python3 upload_to_gitlab.py --folder $UNZIP_DIR --android_version $ANDROID_VERSION

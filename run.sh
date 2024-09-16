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
echo "Downloading $URL..."
python3 download.py --download $URL
FILE=$(get_base_name $URL)
echo "File name is $FILE"
EXTENSION=$(echo ${FILE##*.} | inline-detox)
UNZIP_DIR=${FILE/.$EXTENSION/}

mkdir -p "$UNZIP_DIR"

partition_list="system product system_ext"
# partition_list="system_ext"

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
ls -R
echo "-----------------------------------------------"
cd $UNZIP_DIR
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
echo "-----------------------------------------------"
ls -R
echo "-----------------------------------------------"
cd ..
ls
python3 upload_to_gitlab.py $UNZIP_DIR
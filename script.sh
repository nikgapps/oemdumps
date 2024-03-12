#!/usr/bin/env bash

# Determine which command to use for privilege escalation
if command -v sudo > /dev/null 2>&1; then
    sudo_cmd="sudo"
elif command -v doas > /dev/null 2>&1; then
    sudo_cmd="doas"
else
    echo "Neither sudo nor doas found. Please install one of them."
    # exit 1
fi

echo "Download link: $link"

# download or copy from local?
if echo "$link" | grep -e '^\(https\?\|ftp\)://.*$' > /dev/null; then
    # 1DRV URL DIRECT LINK IMPLEMENTATION
    if echo "$link" | grep -e '1drv.ms' > /dev/null; then
        URL=`curl -I "$link" -s | grep location | sed -e "s/redir/download/g" | sed -e "s/location: //g"`
    else
        URL=$link
    fi
    { type -p aria2c > /dev/null 2>&1 && printf "Downloading File...\n" && aria2c -x16 -j"$(nproc)" "${URL}"; } || { printf "Downloading File...\n" && wget -q --content-disposition --show-progress --progress=bar:force "${URL}" || exit 1; }
    if [[ ! -f "$(echo ${URL##*/} | inline-detox)" ]]; then
        URL=$(wget --server-response --spider "${URL}" 2>&1 | awk -F"filename=" '{print $2}')
    fi
    detox "${URL##*/}"
else
    URL=$(printf "%s\n" "$link")
    [[ -e "$URL" ]] || { echo "Invalid Input" && exit 1; }
fi

ORG=AndroidDumps #your GitHub org name
FILE=$(echo ${URL##*/} | inline-detox)
EXTENSION=$(echo ${URL##*.} | inline-detox)
UNZIP_DIR=${FILE/.$EXTENSION/}

bash "/Firmware_extractor/extractor.sh" "${FILE}" "${UNZIP_DIR}"

PARTITIONS="system systemex system_ext system_other vendor cust odm odm_ext oem factory product modem xrom oppo_product opproduct reserve india my_preload my_odm my_stock my_operator my_country my_product my_company my_engineering my_heytap my_custom my_manifest my_carrier my_region my_bigball my_version special_preload vendor_dlkm odm_dlkm system_dlkm mi_ext"
PARTITIONS="system product system_ext"

cd "${UNZIP_DIR}" || exit
for p in $PARTITIONS; do
    # Try to extract images via fsck.erofs
    if [ -f $p.img ] && [ $p != "modem" ]; then
        echo "Trying to extract $p partition via fsck.erofs."
        /Firmware_extractor/tools/Linux/bin/fsck.erofs --extract="$p" "$p".img
        # Deletes images if they were correctly extracted via fsck.erofs
        if [ -d "$p" ]; then
            rm "$p".img > /dev/null 2>&1
        else
        # Uses 7z if images could not be extracted via fsck.erofs
            if [[ -e "$p.img" ]]; then
                mkdir "$p" 2> /dev/null || rm -rf "${p:?}"/*
                echo "Extraction via fsck.erofs failed, extracting $p partition via 7z"
                7z x "$p".img -y -o"$p"/ > /dev/null 2>&1
                if [ $? -eq 0 ]; then
                    rm "$p".img > /dev/null 2>&1
                else                
                    echo "Couldn't extract $p partition. It might use an unsupported filesystem."
                    echo "For EROFS: make sure you're using Linux 5.4+ kernel."
                    echo "For F2FS: make sure you're using Linux 5.15+ kernel."
                fi
            fi
        fi
    fi
done

ls -R
#!/bin/bash

# Exit on first error
set -e

# Source the virtual environment
source /usr/src/workdir/venv/bin/activate

# Enable debugging to print each command before it's executed
# set -x
# Disabling logging since the script is working fine now, can be re-enabled later for debugging purposes

# Setup SSH directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh
which ssh-keyscan || (apt-get update && apt-get install -y openssh-client)
# Start ssh-agent
eval "$(ssh-agent -s)"

# Function to check if a string is base64 encoded
is_base64() {
  echo "$1" | base64 --decode > /dev/null 2>&1
  return $?
}

# Check if the SSH key is base64 encoded
if is_base64 "$SSH_PRIVATE_KEY"; then
  DECODED_SSH_KEY=$(echo "$SSH_PRIVATE_KEY" | base64 --decode | tr -d '\r')
  echo "SSH_PRIVATE_KEY was base64 encoded and has been decoded."
else
  DECODED_SSH_KEY=$(echo "$SSH_PRIVATE_KEY" | tr -d '\r')
  echo "SSH_PRIVATE_KEY was not base64 encoded and has been used directly."
fi

# Add the decoded SSH private key to the ssh-agent
echo "$DECODED_SSH_KEY" | ssh-add -

# Add SSH keys to known_hosts to avoid prompts
ssh-keyscan -H frs.sourceforge.net >> ~/.ssh/known_hosts || echo "Failed to scan frs.sourceforge.net"
ssh-keyscan -H github.com >> ~/.ssh/known_hosts || echo "Failed to scan github.com"
ssh-keyscan -H gitlab.com >> ~/.ssh/known_hosts || echo "Failed to scan gitlab.com"

# Secure the known_hosts file
chmod 600 ~/.ssh/known_hosts

echo "SSH setup complete."

echo "Setting up Git"

git config --global user.email "$USER_EMAIL"
git config --global user.name "$USER_NAME"
git config --global http.postBuffer 1048576000

git clone git@github.com:nikgapps/oemdumps.git

cd oemdumps

pip3 install -r requirements.txt

URL=$(python3 main.py)
echo "Download link: $URL"
7z --version
if [ -z "$URL" ]; then
    echo "No URL found"
    exit 1
fi

FILE=$(echo ${URL##*/} | inline-detox)
EXTENSION=$(echo ${URL##*.} | inline-detox)
UNZIP_DIR=${FILE/.$EXTENSION/}

echo "GITLAB_TOKEN=$GITLAB_TOKEN" >> .env

python3 payload_dumper.py "extracted/payload.bin"

cd output
PARTITIONS="system product system_ext"
for p in $PARTITIONS; do
    if [[ -e "$p.img" ]]; then
        mkdir "$p" 2> /dev/null || rm -rf "${p:?}"/*
        echo "Trying to extract $p partition via 7z."
        7z x "$p".img -y -o"$p"/ > /dev/null 2>&1
        echo "7z exit status: $?"
        if [ $? -eq 0 ]; then
            rm "$p".img > /dev/null 2>&1
        else
            echo "Failed to extract $p partition via 7z."
        fi
    fi
done

cd ..
ls -R
python3 push_oem_files_on_server.py -N $UNZIP_DIR
cd ..

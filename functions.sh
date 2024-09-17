# functions.sh

# Fetch environment variables if necessary
fetch_env_vars() {
    if [ -z "$GITLAB_TOKEN" ]; then
        echo "GITLAB_TOKEN is not set"
        exit 1
    fi

    CLONE_DIR="/myenv"

    echo "Cloning the private repository..."
    git clone https://oauth2:$GITLAB_TOKEN@gitlab.com/nikgapps/myenv.git $CLONE_DIR

    cd $CLONE_DIR
    pip install -r requirements.txt
    eval "$(python3 main.py)"
    cd ..
}

# Function to check if a string is base64 encoded
is_base64() {
    echo "$1" | base64 --decode >/dev/null 2>&1
    return $?
}

# Function to set up SSH keys
setup_ssh() {
    # Check if the SSH key is base64 encoded
    if is_base64 "$1"; then
        DECODED_SSH_KEY=$(echo "$1" | base64 --decode | tr -d '\r')
        echo "SSH_PRIVATE_KEY was base64 encoded and has been decoded."
    else
        DECODED_SSH_KEY=$(echo "$1" | tr -d '\r')
        echo "SSH_PRIVATE_KEY was not base64 encoded and has been used directly."
    fi
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    which ssh-keyscan || (apt-get update && apt-get install -y openssh-client)
    eval "$(ssh-agent -s)"
    echo "$DECODED_SSH_KEY" | ssh-add -
    ssh-keyscan -H frs.sourceforge.net >>~/.ssh/known_hosts || echo "Failed to scan frs.sourceforge.net"
    ssh-keyscan -H github.com >>~/.ssh/known_hosts || echo "Failed to scan github.com"
    ssh-keyscan -H gitlab.com >>~/.ssh/known_hosts || echo "Failed to scan gitlab.com"
    chmod 600 ~/.ssh/known_hosts
    echo "SSH setup complete."
}

setup_git() {
    git config --global user.email "$USER_EMAIL"
    git config --global user.name "$USER_NAME"
    git config --global http.postBuffer 1048576000
}

get_base_name() {
    echo $(for f1 in ${1//\// }; do [[ "$f1" == *.zip ]] && echo "$f1" && break; done)
}

extract_dat_br() {
    echo "Extracting $1.new.dat.br and converting to $1.img..."
    brotli -d $1.new.dat.br -o $1.new.dat
    python /sdat2img/sdat2img.py $1.transfer.list $1.new.dat $1.img
    rm -rf $1.new.dat.br $1.new.dat $1.transfer.list
    echo "Extraction of $1.new.dat.br complete."
    extract_img_7z $1
}

extract_img_7z() {
    if [ -f $1.img ]; then
        FILE_TYPE=$(file "$1.img")
        echo "Extracting $1.img with type $FILE_TYPE..."
        mkdir -p "$1"
        echo "Trying to extract $1.img using 7z."
        7z x "$1.img" -y -o"$1" >/dev/null 2>&1 || echo "Failed to extract $1.img using 7z."
        echo "Extraction of $1.img complete."
        rm -f "$1.img"
    else
        echo "$1.img not found."
    fi
}

fetch_android_version() {
    case "$1" in
      system)
          build_prop_path="$1/system/build.prop"
          ;;
      product | system_ext)
          build_prop_path="$1/etc/build.prop"
          ;;
      *)
          echo "Unknown partition: $1"
          return 1
          ;;
    esac

    if [ -f "$build_prop_path" ]; then
        VERSION=$(grep "ro.$1.build.version.release" "$build_prop_path" | cut -d '=' -f 2)
        if [ -n "$VERSION" ]; then
            echo "$VERSION"
        else
            echo "Version information not found in $1 partition."
            return 1
        fi
    else
        echo "build.prop not found in the $1 partition."
        return 1
    fi
}


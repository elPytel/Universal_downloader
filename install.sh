#!/bin/bash
# By Pytel

set -e

python_dependencies="requirements.txt"
apt_dependencies="apt-dependencies.txt"
venv_dir="${VENV_DIR:-venv}"

# Load optional local configuration without committing it to the repository.
if [ -f .env ]; then
    # shellcheck disable=SC1091
    source .env
fi

install_python_to_system="${INSTALL_PYTHON_TO_SYSTEM:-false}"

case "$install_python_to_system" in
    true|TRUE|1|yes|YES)
        python_install_command=(sudo python3 -m pip install --break-system-packages)
        ;;
    false|FALSE|0|no|NO)
        if [ ! -x "$venv_dir/bin/python" ]; then
            python3 -m venv "$venv_dir"
        fi
        python_install_command=("$venv_dir/bin/python" -m pip install)
        ;;
    *)
        echo "INSTALL_PYTHON_TO_SYSTEM must be true or false." >&2
        exit 1
        ;;
esac

# Install apt dependencies
sudo apt-get update
if [ -f $apt_dependencies ]; then
    xargs sudo apt-get -y install < $apt_dependencies
fi

# Install Python dependencies
if [ -f $python_dependencies ]; then 
    "${python_install_command[@]}" --upgrade pip
    "${python_install_command[@]}" -r "$python_dependencies"
fi

# Compile language files
localisation="universal_downloader"
for lang in locales/*; do
    if [ -d "$lang/LC_MESSAGES" ]; then
        msgfmt -o "$lang/LC_MESSAGES/$localisation.mo" "$lang/LC_MESSAGES/$localisation.po"
    fi
done

echo "Installation and compilation completed."

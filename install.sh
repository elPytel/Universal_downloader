#!/bin/bash
# By Pytel

python_dependencies="requirements.txt"
apt_dependencies="apt-dependencies.txt"

# Install apt dependencies
sudo apt-get update
if [ -f $apt_dependencies ]; then
    xargs sudo apt-get -y install < $apt_dependencies
fi

# Install Python dependencies
if [ -f $python_dependencies ]; then 
    pip install -r $python_dependencies
fi

# Compile language files
localisation="universal_downloader"
for lang in locales/*; do
    if [ -d "$lang/LC_MESSAGES" ]; then
        msgfmt -o "$lang/LC_MESSAGES/$localisation.mo" "$lang/LC_MESSAGES/$localisation.po"
    fi
done

echo "Installation and compilation completed."

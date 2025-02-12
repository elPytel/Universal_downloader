#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Compile language files
localisation="universal_downloader"
for lang in locales/*; do
    if [ -d "$lang/LC_MESSAGES" ]; then
        msgfmt -o "$lang/LC_MESSAGES/$localisation.mo" "$lang/LC_MESSAGES/$localisation.po"
    fi
done

echo "Installation and compilation completed."

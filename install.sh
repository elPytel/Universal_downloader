
#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Compile language files
for lang in locales/*; do
    if [ -d "$lang/LC_MESSAGES" ]; then
        msgfmt -o "$lang/LC_MESSAGES/universal_downloader.mo" "$lang/LC_MESSAGES/universal_downloader.po"
    fi
done

echo "Installation and compilation completed."

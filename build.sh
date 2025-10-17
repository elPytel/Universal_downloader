#!/bin/bash

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Compile .po -> .mo if msgfmt is available
if command -v msgfmt >/dev/null 2>&1; then
    echo "msgfmt found, compiling .po -> .mo..."
    for d in locales/*; do
        if [ -d "$d" ] && [ -f "$d/LC_MESSAGES/universal_downloader.po" ]; then
            echo "Compiling \"$d/LC_MESSAGES/universal_downloader.po\""
            msgfmt -o "$d/LC_MESSAGES/universal_downloader.mo" "$d/LC_MESSAGES/universal_downloader.po" || echo "Warning: msgfmt failed for $d"
        fi
    done
else
    echo "msgfmt not found in PATH — skipping .po -> .mo compilation. Install gettext (e.g. 'sudo apt install gettext') to enable compilation."
fi

# Build the application using pyinstaller
pyinstaller --onefile --windowed \
    --icon=assets/icon.ico \
    --add-data "assets/icon.png:assets" \
    --add-data "locales:locales" \
    --name universal_downloader \
    gui.py

# Deactivate the virtual environment
deactivate
echo "Done."
#!/bin/bash

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

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
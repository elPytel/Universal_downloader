#!/bin/bash

OUTPUT_DIR="./docs"

pdoc ./gui.py ./main.py ./src/downloader/datoid.py ./src/downloader/sdilej.py ./src/downloader/prehrajto.py ./src/download/page_search.py -o $OUTPUT_DIR

echo "Documentation generated in $OUTPUT_DIR"
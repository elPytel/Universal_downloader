:: filepath: /e:/Git/Universal_downloader/build.bat
@echo off

:: Create a virtual environment
echo Creating a virtual environment...
python -m venv venv

:: Activate the virtual environment
call venv\Scripts\activate

:: Upgrade pip
echo Upgrading pip...
pip install --upgrade pip

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

:: Build the application using pyinstaller
echo Building the application...
pyinstaller --onefile --windowed ^
    --icon=assets/icon.ico ^
    --add-data "assets/icon.png;assets" ^
    --add-data "locales;locales" ^
    --name universal_downloader ^
    gui.py

:: Deactivate the virtual environment
echo Deactivating the virtual environment...
deactivate
echo Build complete!
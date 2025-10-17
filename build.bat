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

:: Compile .po -> .mo if msgfmt is available
where msgfmt >nul 2>&1
if %ERRORLEVEL%==0 (
    echo msgfmt found, compiling .po -> .mo...
    for /d %%D in (locales\*) do (
        if exist "%%D\LC_MESSAGES\universal_downloader.po" (
            echo Compiling "%%D\LC_MESSAGES\universal_downloader.po"
            msgfmt -o "%%D\LC_MESSAGES\universal_downloader.mo" "%%D\LC_MESSAGES\universal_downloader.po"
            if ERRORLEVEL 1 echo Warning: msgfmt failed for %%D
        )
    )
) else (
    echo msgfmt not found in PATH — skipping .po -> .mo compilation. Make sure .mo files are included in the build.
)

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
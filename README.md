# Universal downloader

Slouží pro stahování souborů z webu: [sdilej.cz](sdilej.cz).

## Instalace
Závislosti jsou uvedeny v souboru `requirements.txt`. Pro jejich instalaci použijte následující příkaz:
```bash
pip install -r requirements.txt
```

## Použití v příkazové řádce

### Help
```bash
main.py --help
usage: main.py [-h] [-s SEARCH] [-t {all,video,audio,archive,images}] [-T {relevance,most_downloaded,newest,biggest,smallest}] [-d] [-f FILE] [-F FOLDER] [-v] [-D] [-g]

Download files from internet.

options:
  -h, --help            show this help message and exit
  -s SEARCH, --search SEARCH
                        Search for files.
  -t {all,video,audio,archive,images}, --file-type {all,video,audio,archive,images}
                        Type of files to search for.
  -T {relevance,most_downloaded,newest,biggest,smallest}, --search-type {relevance,most_downloaded,newest,biggest,smallest}
                        Search format.
  -d, --download        Download the found files.
  -f FILE, --file FILE  File to download.
  -F FOLDER, --folder FOLDER
                        Folder to download to.
  -v, --verbose         Verbose mode.
  -D, --debug           Debug mode.
  -g, --tui             Start TUI.
```

### Vyhledání souborů
```bash
main.py --search "název souboru" --file-type "audio" --search-type "smallest"
```
Vyhledané soubory se uloží do souboru `files.json`. 

> [!tip]
> Nyní je můžete manuálně projít a odstranit, které soubory nechcete stáhnout.

### Stažení souborů
```bash
main.py --download
```
Tento příkaz projde obsah souboru `files.json` a stáhne všechny soubory, které jsou v něm uvedeny.

## Použití v TUI

```bash
main.py --tui
```

> [!warning]
> PTG nefunguje pod OS Windows.

## TODO:
https://realpython.com/python-download-file-from-url/
https://github.com/bczsalba/pytermgui/tree/master/examples
https://ptg.bczsalba.com/reference/pytermgui/enums/#pytermgui.enums.SizePolicy
https://ptg.bczsalba.com/reference/pytermgui/window_manager/window/#pytermgui.window_manager.window.Window.is_modal
https://ptg.bczsalba.com/widgets/attrs/
https://ptg.bczsalba.com/widgets/attrs/#parent-align
https://www.youtube.com/watch?v=rMPkVpo529s

https://github.com/ceccopierangiolieugenio/pyTermTk/tree/main
https://github.com/Textualize/textual?tab=readme-ov-file
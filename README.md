# Documents salvage ship
Script to salvage documents.  
Using OCR, move only the photos that contain recognizable characters to a separate folder.

## Usage

```sh
# python main {target dir} {language} {Destination document path} {If exists specify a saved file path of already checked files}
python main.py . jpn ./doc-files documents-salvage-ship_already-checked-files.txt
```

## Suspend and Resume

If you interrupt the process with Ctrl + C, a file named `documents-salvage-ship_already-checked-files.txt` will be created at the current location of the path you executed.  
Here you will find a comma-separated list of files that have already been checked.  
If you want to skip checking files that have already been checked next time, you must specify the path to this file as well.
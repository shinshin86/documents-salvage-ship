from PIL import Image
import sys
import argparse
import pyocr
import pyocr.builders
import pathlib
import os
from os import path
import re
import shutil
import asyncio
import functools
import threading


# global vars
checked_files = []
already_checked_files = []

# support image files
pattern = ".*\.(jpg|jpeg|png|gif|bmp)"


def is_doc_image(img, lang, tool):
    try:
        image = Image.open(img)
    except FileNotFoundError:
        print("Target image file not found")
        return False

    try:
        # 4 Assume a single column of text of variable sizes.(tesseract --help-extra)
        builder = pyocr.builders.TextBuilder(tesseract_layout=4)

        txt = tool.image_to_string(
            image,
            lang,
            builder=builder
        )

        return txt != ""
    except Exception as e:
        print("ERROR: TesseractError")
        print(e)
        return False


async def main(dir, lang, mvdir, checkedfiles):
    lock = threading.Lock()

    os.makedirs(mvdir, exist_ok=True)

    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("ERROR: Not found OCR Tool")
        sys.exit(1)

    tool = tools[0]
    print("Using OCR Tool: '%s'" % (tool.get_name()))

    image_files = [f for f in os.listdir(path=dir) if re.search(pattern, f, re.IGNORECASE)]
    print("check file count: ", len(image_files))

    document_files = []

    loop = asyncio.get_event_loop()

    if checkedfiles is not None:
        with open(path.abspath(checkedfiles)) as file:
            already_checked_files = file.read().split(',')
        print("Exists already checked files: ", already_checked_files)
    
    for f in image_files:
        if checkedfiles is not None:
            if f in already_checked_files:
                continue

        print("check file: ", f)
        asbpath = path.abspath(f)
        is_doc = await loop.run_in_executor(None, functools.partial(
            is_doc_image, asbpath, lang, tool
        ))

        with lock:
            if is_doc is True:
                result = shutil.move(path.abspath(f), path.abspath(mvdir))
                print("move document file: ", path.abspath(f), " => ", result)
            checked_files.append(f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Document image search")
    parser.add_argument("dir", metavar="dir", type=pathlib.Path, help="Target dir path")
    parser.add_argument("lang", metavar="lang", help="Language")
    parser.add_argument("mvdir", metavar="mvdir", type=pathlib.Path, help="Destination path of the document")
    parser.add_argument("checkedfiles", metavar="checkedfiles", type=pathlib.Path, default=None, nargs='?', help="Path to text file with list of files already checked")
    args = parser.parse_args()

    try:
        while True:
            asyncio.run(main(args.dir, args.lang, args.mvdir, args.checkedfiles))
    except KeyboardInterrupt:
        print("Quit salvage!")
        print("Save checked files...")
        save_text = ""
        if args.checkedfiles is not None:
            with open(path.abspath(args.checkedfiles)) as file:
                save_text += file.read().rstrip()

        if save_text != "":
            save_text += ","

        save_text +=  ",".join(checked_files)
        save_file_name = "documents-salvage-ship_already-checked-files.txt"
        with open(save_file_name, "w") as file:
            file.write(save_text)
            print("saved file:", save_file_name)
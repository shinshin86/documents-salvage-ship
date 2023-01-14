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


# support image files
pattern = ".*\.(jpg|jpeg|png|gif|bmp)"


def is_doc_image(img, lang):
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Document image search")
    parser.add_argument("dir", metavar="dir", type=pathlib.Path, help="Target dir path")
    parser.add_argument("lang", metavar="lang", help="Language")
    parser.add_argument("mvdir", metavar="mvdir", type=pathlib.Path, help="Destination path of the document")
    args = parser.parse_args()

    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("ERROR: Not found OCR Tool")
        sys.exit(1)

    tool = tools[0]
    print("Using OCR Tool: '%s'" % (tool.get_name()))

    image_files = [f for f in os.listdir(path=args.dir) if re.search(pattern, f, re.IGNORECASE)]
    print("check file count: ", len(image_files))

    document_files = []
    for f in image_files:
        print("check file: ", f)
        if is_doc_image(path.abspath(f), args.lang) is True:
            document_files.append(path.abspath(f))

    os.makedirs(args.mvdir, exist_ok=True)
    for doc in document_files:
        result = shutil.move(doc, path.abspath(args.mvdir))
        print("move document file: ", doc, " => ", result)
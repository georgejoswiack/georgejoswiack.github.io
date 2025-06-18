from pyvz2rijndael import RijndaelCBC
import base64
import zlib
import struct
import sys
import os
import json
import hashlib

key = "65bd1b2305f46eb2806b935aab7630bb"
tool = RijndaelCBC(key=key, block_size=24)
magic = 0xDEADFED4

def decode(data: bytes):
    step1 = base64.b64decode(data)[2:]
    step2 = tool.decrypt(step1)[8:]
    step3 = zlib.decompress(step2)
    return step3

def encode(data: bytes):
    step1 = struct.pack("<I", magic) + struct.pack("<I", len(data)) + zlib.compress(data)
    step2 = tool.encrypt(step1)
    step3 = base64.b64encode(b"\x10\0" + step2)
    return step3

def process_translation(input_file, output_dir):
    # Reading input file
    with open(input_file, "rb") as f:
        translation = f.read()

    # Check if the file already has a UTF-8 BOM
    if translation.startswith(b'\xEF\xBB\xBF'):
        # If it has a BOM, remove it before decoding
        translation_str = translation[3:].decode('utf-8')
    else:
        # If it doesn't have a BOM, decode directly
        translation_str = translation.decode('utf-8')

    # Encode the content to UTF-8-BOM (add BOM if not already present)
    translation_utf8_bom = translation_str.encode('utf-8-sig')

    # Generating pvz2_l.txt
    pvz2_content = encode(translation_utf8_bom)
    with open(os.path.join(output_dir, "pvz2_l.txt"), "wb") as f:
        f.write(pvz2_content)

    # Generating content to file_lists.txt
    h = hashlib.md5(translation_utf8_bom).hexdigest()
    d = {
        "File": {
            "Name": "pvz2_l.txt",
            "Hash": h
        }
    }

    # Generating file_list.txt
    file_list_content = encode(json.dumps(d).encode('utf-8'))
    with open(os.path.join(output_dir, "file_list.txt"), "wb") as f:
        f.write(file_list_content)

if __name__ == '__main__':
    raw_file = sys.argv[1]  # path to raw lawnstrings file
    out_dir = sys.argv[2]  # path to output directory

    os.makedirs(out_dir, exist_ok=True)
    process_translation(raw_file, out_dir)
